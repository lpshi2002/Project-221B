"""Deterministic gate for a solved case: schema, ID integrity, quote grounding.

Principle 1 of the concept doc ("conclusions come only from the input") is
enforced here rather than trusted to the model: every quote must be found in
the case text, and every cited ID must exist.
"""

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ValidationError

from .schema import CaseModel, Verdict

_QUOTE_CHARS = str.maketrans({c: '"' for c in "'‘’‚‛“”„‟`´"})
_ELLIPSIS = re.compile(r"\.\.\.|…")


def normalize(text: str) -> str:
    text = text.translate(_QUOTE_CHARS).replace(" ", " ").lower()
    text = re.sub(r"[-‐‑‒–—―]+", "-", text)
    return re.sub(r"\s+", " ", text).strip()


def is_grounded(quote: str, source: str) -> bool:
    """True if the quote's fragments (split on ellipses) appear in order in source."""
    haystack = normalize(source)
    pos = 0
    fragments = [f.strip(' "-,.;:') for f in _ELLIPSIS.split(normalize(quote))]
    fragments = [f for f in fragments if f]
    if not fragments:
        return False
    for frag in fragments:
        idx = haystack.find(frag, pos)
        if idx < 0:
            return False
        pos = idx + len(frag)
    return True


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    quotes: int = 0
    ungrounded: list[str] = field(default_factory=list)
    dangling: list[str] = field(default_factory=list)
    knowledge: list[str] = field(default_factory=list)  # common_knowledge claims, not grounded in the text

    @property
    def ok(self) -> bool:
        return not self.errors

    def check_quote(self, where: str, quote: str, source: str) -> None:
        self.quotes += 1
        if not is_grounded(quote, source):
            self.ungrounded.append(where)
            self.errors.append(f"{where}: quote not found verbatim in case text: {quote[:80]!r}")

    def check_refs(self, where: str, refs: list[str], known: set[str]) -> None:
        for ref in refs:
            if ref not in known:
                self.dangling.append(f"{where} -> {ref}")
                self.errors.append(f"{where}: unknown ID {ref!r}")


def _load(path: Path, model: type[BaseModel], report: Report):
    try:
        return model.model_validate_json(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        report.errors.append(f"{path.name}: missing")
    except ValidationError as e:
        for err in e.errors():
            loc = ".".join(str(x) for x in err["loc"])
            report.errors.append(f"{path.name}: {loc}: {err['msg']}")
    return None


def _unique(report: Report, where: str, ids: list[str]) -> set[str]:
    seen = set()
    for i in ids:
        if i in seen:
            report.errors.append(f"{where}: duplicate ID {i!r}")
        seen.add(i)
    return seen


def check_case_model(cm: CaseModel, text: str, report: Report) -> dict[str, str]:
    """Check the case model; return evidence ID -> kind."""
    people = _unique(report, "case_model.people", [p.id for p in cm.people])
    evidence = _unique(report, "case_model.evidence", [e.id for e in cm.evidence])
    _unique(report, "case_model.events", [t.id for t in cm.events])
    _unique(report, "case_model.contradictions", [c.id for c in cm.contradictions])
    for e in cm.evidence:
        if e.kind == "common_knowledge":
            report.knowledge.append(f"case_model.{e.id}")
        else:
            report.check_quote(f"case_model.{e.id}", e.quote, text)
    for p in cm.people:
        report.check_refs(f"case_model.{p.id}.statements", p.statements, evidence)
    for t in cm.events:
        report.check_refs(f"case_model.{t.id}.people", t.people, people)
        report.check_refs(f"case_model.{t.id}.evidence", t.evidence, evidence)
    for c in cm.contradictions:
        report.check_refs(f"case_model.{c.id}.evidence", c.evidence, evidence)
        report.check_refs(f"case_model.{c.id}.implicates", c.implicates, people)
    return {e.id: e.kind for e in cm.evidence}


def check_verdict(v: Verdict, case: dict, evidence: dict[str, str] | None, report: Report,
                  anomalies: set[str] = frozenset()) -> None:
    options = set(case["options"])
    if v.case_id != case["id"]:
        report.errors.append(f"verdict.case_id {v.case_id!r} != {case['id']!r}")
    if v.answer != "insufficient" and v.answer not in options:
        report.errors.append(f"verdict.answer {v.answer!r} not in options {sorted(options)}")
    if v.answer == "insufficient" and not v.missing_evidence:
        report.errors.append("verdict: 'insufficient' requires missing_evidence")

    for i, k in enumerate(v.key_evidence):
        if k.common_knowledge or (evidence or {}).get(k.id) == "common_knowledge":
            report.knowledge.append(f"verdict.key_evidence[{i}]")
        else:
            report.check_quote(f"verdict.key_evidence[{i}]", k.quote, case["text"])
        if evidence is not None:
            if k.id is None:
                report.errors.append(f"verdict.key_evidence[{i}]: id required when a case model exists")
            else:
                report.check_refs(f"verdict.key_evidence[{i}]", [k.id], evidence)

    if v.method == "baseline":
        return
    covered = [h.option for h in v.hypotheses]
    if sorted(covered) != sorted(options):
        report.errors.append(f"verdict.hypotheses must cover each option once: got {covered}, need {sorted(options)}")
    for h in v.hypotheses:
        report.check_refs(f"verdict.hypotheses[{h.option}].supporting", h.supporting, set(evidence or {}))
        report.check_refs(f"verdict.hypotheses[{h.option}].refuting", h.refuting, set(evidence or {}))
        for ref in h.unexplained:
            if ref not in anomalies:
                report.errors.append(f"verdict.hypotheses[{h.option}].unexplained: {ref!r} is not anomaly evidence")
        if h.status == "eliminated" and not h.refuting:
            report.errors.append(f"verdict.hypotheses[{h.option}]: eliminated without refuting evidence")
    leading = [h.option for h in v.hypotheses if h.status == "leading"]
    if v.answer != "insufficient" and leading != [v.answer]:
        report.errors.append(f"verdict: exactly one leading hypothesis must match answer {v.answer!r}, got {leading}")
    for i, c in enumerate(v.challenges):
        report.check_refs(f"verdict.challenges[{i}]", c.evidence, set(evidence or {}))
    if v.method == "full" and v.answer != "insufficient" and not any(c.target == v.answer for c in v.challenges):
        report.errors.append("verdict: method 'full' requires at least one challenge against the answer")


def validate(case_dir: Path, log: bool = True) -> Report:
    report = Report()
    case = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    verdict = _load(case_dir / "verdict.json", Verdict, report)

    if verdict is not None and verdict.method != case["method"]:
        report.errors.append(f"verdict.method {verdict.method!r} != assigned method {case['method']!r}")

    evidence, anomalies = None, set()
    if case["method"] != "baseline" or (case_dir / "case_model.json").exists():
        cm = _load(case_dir / "case_model.json", CaseModel, report)
        if cm is not None:
            evidence = check_case_model(cm, case["text"], report)
            anomalies = {e.id for e in cm.evidence if e.anomaly}
    if verdict is not None:
        check_verdict(verdict, case, evidence, report, anomalies)

    if log:
        entry = {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "ok": report.ok, **asdict(report)}
        with (case_dir / "validation_log.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return report
