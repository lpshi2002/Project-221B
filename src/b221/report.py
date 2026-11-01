"""Render report.md from a case directory's JSON outputs.

The report is a view over verdict.json / case_model.json, so it is generated
rather than written by the agent: it can't drift from what was validated.
"""

import json
from pathlib import Path

from .schema import CaseModel, Verdict

_STATUS = {"leading": "유력", "viable": "가능", "eliminated": "제외"}
_CHECK = {"attack": "유력 가설 공격", "attribution": "발언 귀속", "exclusion": "제외 검사", "exempted": "면제된 사람",
          "witness": "목격자 시선", "runner_up": "2위 가설 재건", "diagnosticity": "진단력", "assumption": "핵심 가정",
          "linchpin": "핵심 증거 민감도", "anomaly": "설명 안 된 이상 사실", "absence": "있어야 할 흔적"}


def render(case_dir: Path) -> str:
    case = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    v = Verdict.model_validate_json((case_dir / "verdict.json").read_text(encoding="utf-8"))
    cm_path = case_dir / "case_model.json"
    cm = CaseModel.model_validate_json(cm_path.read_text(encoding="utf-8")) if cm_path.exists() else None
    evidence = {e.id: e for e in cm.evidence} if cm else {}
    people = {p.id: p.name for p in cm.people} if cm else {}

    if v.answer == "insufficient":
        conclusion = "증거 부족 — 지목하지 않음"
    else:
        conclusion = f"({v.answer}) {case['options'][v.answer]}"
    out = [
        f"# {case['title']} — 추리 보고서",
        "",
        f"**결론:** {conclusion} · 확신도 {v.confidence:.2f} · 방식 `{v.method}`",
        "",
        "## 추론",
        "",
        v.reasoning,
        "",
        "## 핵심 근거",
        "",
    ]
    for k in v.key_evidence:
        tag = f"**{k.id}** " if k.id else ""
        if k.common_knowledge or (evidence.get(k.id) and evidence[k.id].kind == "common_knowledge"):
            out.append(f"- {tag}(상식) {k.quote} — {k.why}")
        else:
            out.append(f"- {tag}“{k.quote}” — {k.why}")

    if cm and (cm.events or cm.contradictions):
        out += ["", "## 타임라인·모순", ""]
        for t in cm.events:
            who = ", ".join(people.get(p, p) for p in t.people)
            out.append(f"- `{t.time}` {t.description}" + (f" ({who})" if who else "") + f" [{', '.join(t.evidence)}]")
        for c in cm.contradictions:
            who = ", ".join(people.get(p, p) for p in c.implicates)
            out.append(f"- ⚠ **{c.id}** {c.description} [{', '.join(c.evidence)}]" + (f" → {who}" if who else ""))

    if v.hypotheses:
        out += ["", "## 가설 비교", "",
                "| 선택지 | 상태 | 가능성 | 지지 | 반대 | 설명 못 한 이상 사실 | 시나리오 |", "|---|---|---|---|---|---|---|"]
        for h in sorted(v.hypotheses, key=lambda h: -h.likelihood):
            out.append(
                f"| ({h.option}) {case['options'][h.option]} | {_STATUS[h.status]} | {h.likelihood:.2f} "
                f"| {', '.join(h.supporting) or '-'} | {', '.join(h.refuting) or '-'} "
                f"| {', '.join(h.unexplained) or '-'} | {h.scenario} |"
            )
        missing = [(h.option, m) for h in v.hypotheses for m in h.expected_missing]
        if missing:
            out += ["", "**있어야 하는데 없는 흔적:**"]
            out += [f"- ({o}) {m}" for o, m in missing]

    if v.challenges:
        out += ["", "## 반론과 대응", ""]
        for c in v.challenges:
            mark = "버팀" if c.survived else "무너짐"
            label = f" [{_CHECK[c.check]}]" if c.check else ""
            out.append(f"- **({c.target}) 공격{label}:** {c.attack}  \n  **{mark}:** {c.resolution}")

    if v.speculation or v.missing_evidence:
        out += ["", "## 남은 불확실성", ""]
        out += [f"- (추측) {s}" for s in v.speculation]
        out += [f"- (필요한 증거) {m}" for m in v.missing_evidence]

    if evidence:
        out += ["", "<details><summary>증거 목록</summary>", ""]
        for e in evidence.values():
            flag = ", 이상 사실" if e.anomaly else ""
            out.append(f"- **{e.id}** [{e.kind}, 신뢰도 {e.reliability}{flag}] “{e.quote}” — {e.shows} / 증명하지 않음: {e.does_not_show}")
        out += ["", "</details>"]
    return "\n".join(out) + "\n"


def write(case_dir: Path) -> Path:
    path = case_dir / "report.md"
    path.write_text(render(case_dir), encoding="utf-8")
    return path
