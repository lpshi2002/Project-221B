"""b221 — deterministic tools for the 221B harness.

The reasoning itself is done by the agent (Claude Code / Codex) following
.agents/skills/221b-investigate; this CLI only prepares case files, gates the
agent's output, and scores runs.
"""

import argparse
import hashlib
import json
import random
import string
import sys
from datetime import datetime
from pathlib import Path

from . import ROOT, checks, dataset, report, score
from .schema import CaseModel, Verdict

RUNS = ROOT / "runs"
SKILL = ROOT / ".agents" / "skills" / "221b-investigate" / "SKILL.md"
METHODS = ["baseline", "structured", "full"]


def _case_md(case: dict) -> str:
    opts = "\n".join(f"- ({k}) {v}" for k, v in case["options"].items())
    return (
        f"# {case['id']} — {case['title']}\n\n"
        f"Method: **{case['method']}**\n\n"
        f"## Question\n\n{case['question']}\n\n## Options\n\n{opts}\n\n## Case text\n\n{case['text']}\n"
    )


def _write_case(case_dir: Path, case: dict) -> None:
    case_dir.mkdir(parents=True, exist_ok=False)
    (case_dir / "case.json").write_text(json.dumps(case, ensure_ascii=False, indent=2), encoding="utf-8")
    (case_dir / "case.md").write_text(_case_md(case), encoding="utf-8")


def cmd_fetch(_args) -> int:
    dataset.fetch()
    print(f"saved {dataset.CSV_PATH} ({len(dataset.load())} puzzles)")
    return 0


def cmd_prepare(args) -> int:
    puzzles = dataset.load()
    if args.ids:
        index = {p.id: p for p in puzzles}
        chosen = [index[i] for i in args.ids.split(",")]
    elif args.hardest:
        ranked = sorted(puzzles, key=lambda p: (p.solve_rate, p.id))
        chosen = sorted(ranked[args.skip : args.skip + args.n], key=lambda p: p.id)
    else:
        chosen = sorted(random.Random(args.seed).sample(puzzles, args.n), key=lambda p: p.id)
    run = args.run or f"{datetime.now():%Y%m%d-%H%M}-{args.method}"
    run_dir = RUNS / run
    run_dir.mkdir(parents=True, exist_ok=False)
    for p in chosen:
        # The answer and the author's solution never enter the case directory.
        _write_case(run_dir / p.id, {
            "id": p.id, "title": p.title, "method": args.method, "text": p.text, "options": p.options,
            "question": "The story ends with a mystery. Which option answers it?",
        })
    selection = "ids" if args.ids else f"hardest[{args.skip}:{args.skip + args.n}]" if args.hardest else f"seed={args.seed}"
    meta = {
        "method": args.method, "ids": [p.id for p in chosen], "selection": selection,
        # which version of the reasoning procedure the detectives will read
        "skill_sha": hashlib.sha256(SKILL.read_bytes()).hexdigest()[:12],
        "created": datetime.now().isoformat(),
    }
    (run_dir / "run.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(run_dir.relative_to(ROOT))
    for p in chosen:
        print(f"  {(run_dir / p.id).relative_to(ROOT)}")
    return 0


def cmd_new(args) -> int:
    suspects = [s.strip() for s in args.suspects.split(";") if s.strip()]
    if not 2 <= len(suspects) <= 26:
        print("need 2-26 suspects separated by ';'", file=sys.stderr)
        return 2
    case_dir = RUNS / "adhoc" / args.name
    _write_case(case_dir, {
        "id": args.name, "title": args.title or args.name, "method": args.method,
        "text": Path(args.text).read_text(encoding="utf-8").strip(),
        "options": dict(zip(string.ascii_lowercase, suspects)),
        "question": args.question,
    })
    print(case_dir.relative_to(ROOT))
    return 0


def cmd_validate(args) -> int:
    report = checks.validate(Path(args.case_dir), log=not args.no_log)
    if report.ok:
        print(f"PASS — {report.quotes} quotes grounded, all IDs resolve")
        return 0
    print(f"FAIL — {len(report.errors)} issue(s):")
    for e in report.errors:
        print(f"  - {e}")
    return 1


def cmd_report(args) -> int:
    print(report.write(Path(args.case_dir)))
    return 0


def cmd_score(args) -> int:
    puzzles = dataset.by_id()
    results = [score.score_run(Path(r), puzzles) for r in args.runs]
    out = score.render(results)
    print(out)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(out, encoding="utf-8")
    return 0


def cmd_schema(args) -> int:
    model = {"case_model": CaseModel, "verdict": Verdict}[args.which]
    print(json.dumps(model.model_json_schema(), indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="b221", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("fetch", help="download the True Detective dataset into data/").set_defaults(fn=cmd_fetch)

    p = sub.add_parser("prepare", help="create a run with blinded case directories")
    p.add_argument("--method", choices=METHODS, required=True)
    p.add_argument("--n", type=int, default=10)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--ids", help="comma-separated puzzle IDs (overrides --n/--seed)")
    p.add_argument("--hardest", action="store_true", help="take the N puzzles with the lowest human solve rate")
    p.add_argument("--skip", type=int, default=0, help="with --hardest: skip the K hardest (for a held-out set)")
    p.add_argument("--run", help="run name (default: timestamp-method)")
    p.set_defaults(fn=cmd_prepare)

    p = sub.add_parser("new", help="create an ad-hoc case from your own text")
    p.add_argument("name")
    p.add_argument("--text", required=True, help="file with the case text")
    p.add_argument("--suspects", required=True, help="'A; B; C' — become options a, b, c")
    p.add_argument("--title")
    p.add_argument("--question", default="Who is responsible?")
    p.add_argument("--method", choices=METHODS, default="full")
    p.set_defaults(fn=cmd_new)

    p = sub.add_parser("validate", help="gate a case directory (schema, IDs, quote grounding)")
    p.add_argument("case_dir")
    p.add_argument("--no-log", action="store_true", help="do not record this attempt")
    p.set_defaults(fn=cmd_validate)

    p = sub.add_parser("report", help="render report.md from verdict.json / case_model.json")
    p.add_argument("case_dir")
    p.set_defaults(fn=cmd_report)

    p = sub.add_parser("score", help="score one or more runs against the answer key")
    p.add_argument("runs", nargs="+")
    p.add_argument("--out", help="also write the markdown table here")
    p.set_defaults(fn=cmd_score)

    p = sub.add_parser("schema", help="print a JSON schema")
    p.add_argument("which", choices=["case_model", "verdict"])
    p.set_defaults(fn=cmd_schema)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
