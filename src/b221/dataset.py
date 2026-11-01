"""True Detective dataset (Del & Fishel, 2023): download and load.

The puzzles come from 5minutemystery.com and may only be used for academic
research, so the data lives in the git-ignored ``data/`` directory.
"""

import csv
import io
import re
import urllib.request
import zipfile
from dataclasses import dataclass

from . import ROOT

DATA_URL = "https://github.com/TartuNLP/true-detective/raw/main/data/data.zip"
DATA_DIR = ROOT / "data" / "true-detective"
CSV_PATH = DATA_DIR / "detective-puzzles.csv"

_OPTION = re.compile(r"\(([a-z])\)\s*(.+?)\s*(?=;\s*\([a-z]\)|$)")


@dataclass(frozen=True)
class Puzzle:
    id: str
    title: str
    text: str
    options: dict[str, str]  # letter -> option text
    answer: str  # option letter
    outcome: str  # golden explanation from the original author
    solve_rate: float  # % of human attempts that were correct
    attempts: int


def fetch() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(DATA_URL, timeout=60) as resp:
        payload = resp.read()
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        CSV_PATH.write_bytes(zf.read("data/detective-puzzles.csv"))


def parse_options(raw: str) -> dict[str, str]:
    return {letter: text for letter, text in _OPTION.findall(raw.strip())}


def load() -> list[Puzzle]:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"{CSV_PATH} not found — run `uv run b221 fetch` first")
    puzzles = []
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            options = parse_options(row["answer_options"])
            answer = re.match(r"\s*\(([a-z])\)", row["answer"])
            if not answer or answer.group(1) not in options:
                raise ValueError(f"row {i}: answer {row['answer']!r} not among options")
            puzzles.append(
                Puzzle(
                    id=f"td-{i:03d}",
                    title=row["case_name"].strip(),
                    text=row["mystery_text"].strip(),
                    options=options,
                    answer=answer.group(1),
                    outcome=row["outcome"].strip(),
                    solve_rate=float(row["solve_rate"]),
                    attempts=int(row["attempts"]),
                )
            )
    return puzzles


def by_id() -> dict[str, Puzzle]:
    return {p.id: p for p in load()}
