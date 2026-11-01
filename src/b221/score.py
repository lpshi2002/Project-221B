"""Score solved runs against the answer key (prototype-221B.md §7 metrics)."""

import json
from dataclasses import dataclass
from pathlib import Path

from .dataset import Puzzle
from .schema import Verdict


@dataclass
class CaseScore:
    id: str
    answer: str  # predicted, or "-" if no valid verdict
    truth: str
    correct: bool
    confidence: float | None
    gate_ok: bool  # latest validation passed
    first_quotes: int  # quotes checked on first validation
    first_ungrounded: int
    first_dangling: int
    knowledge: int  # common_knowledge claims in the final state (not grounded in the text)
    attempts: int  # validation runs until the final state
    human_solve_rate: float


def _log(case_dir: Path) -> list[dict]:
    path = case_dir / "validation_log.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def score_case(case_dir: Path, puzzle: Puzzle) -> CaseScore:
    log = _log(case_dir)
    first = log[0] if log else {"quotes": 0, "ungrounded": [], "dangling": []}
    last = log[-1] if log else {}
    try:
        v = Verdict.model_validate_json((case_dir / "verdict.json").read_text(encoding="utf-8"))
        answer, confidence = v.answer, v.confidence
    except (FileNotFoundError, ValueError):
        answer, confidence = "-", None
    return CaseScore(
        id=puzzle.id,
        answer=answer,
        truth=puzzle.answer,
        correct=answer == puzzle.answer,
        confidence=confidence,
        gate_ok=bool(log) and log[-1]["ok"],
        first_quotes=first["quotes"],
        first_ungrounded=len(first["ungrounded"]),
        first_dangling=len(first["dangling"]),
        knowledge=len(last.get("knowledge", [])),
        attempts=len(log),
        human_solve_rate=puzzle.solve_rate,
    )


def score_run(run_dir: Path, puzzles: dict[str, Puzzle]) -> tuple[dict, list[CaseScore]]:
    meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    cases = [score_case(run_dir / cid, puzzles[cid]) for cid in meta["ids"]]
    n = len(cases)
    quotes = sum(c.first_quotes for c in cases)
    scored = [c for c in cases if c.confidence is not None]
    summary = {
        "run": run_dir.name,
        "method": meta["method"],
        "n": n,
        "accuracy": sum(c.correct for c in cases) / n,
        "abstained": sum(c.answer == "insufficient" for c in cases),
        "no_verdict": sum(c.answer == "-" for c in cases),
        "gate_pass": sum(c.gate_ok for c in cases),
        "first_pass_ungrounded_rate": (sum(c.first_ungrounded for c in cases) / quotes) if quotes else 0.0,
        "first_pass_dangling": sum(c.first_dangling for c in cases),
        "knowledge": sum(c.knowledge for c in cases),
        "brier": (sum((c.confidence - c.correct) ** 2 for c in scored) / len(scored)) if scored else None,
        "human_solve_rate": sum(c.human_solve_rate for c in cases) / n / 100,
    }
    return summary, cases


def _pct(x: float) -> str:
    return f"{x * 100:.0f}%"


def render(results: list[tuple[dict, list[CaseScore]]]) -> str:
    lines = [
        "| run | method | n | accuracy | abstained | gate pass | 1st-pass ungrounded quotes | 1st-pass dangling IDs "
        "| common-knowledge claims | Brier | human solve rate |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for s, _ in results:
        brier = "-" if s["brier"] is None else f"{s['brier']:.3f}"
        lines.append(
            f"| {s['run']} | {s['method']} | {s['n']} | {_pct(s['accuracy'])} | {s['abstained']} "
            f"| {s['gate_pass']}/{s['n']} | {_pct(s['first_pass_ungrounded_rate'])} | {s['first_pass_dangling']} "
            f"| {s['knowledge']} | {brier} | {_pct(s['human_solve_rate'])} |"
        )
    for s, cases in results:
        lines += ["", f"### {s['run']} ({s['method']})", "",
                  "| case | answer | truth | ok | conf | gate | validations | human |", "|---|---|---|---|---|---|---|---|"]
        for c in cases:
            conf = "-" if c.confidence is None else f"{c.confidence:.2f}"
            lines.append(
                f"| {c.id} | {c.answer} | {c.truth} | {'✓' if c.correct else '✗'} | {conf} "
                f"| {'pass' if c.gate_ok else 'FAIL'} | {c.attempts} | {c.human_solve_rate:.0f}% |"
            )
    return "\n".join(lines) + "\n"
