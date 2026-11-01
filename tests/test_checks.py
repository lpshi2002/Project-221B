import json

import pytest

from b221 import checks
from b221.dataset import Puzzle, parse_options
from b221.score import score_case

TEXT = (
    "Mrs. Hale said, “I was at the bakery until nine.” The bakery closes at 8:30 -- every "
    "regular knows that. Tom's boots were caked in red clay, the same clay as the garden bed "
    "under the broken window. Ann was on the phone with her sister all evening."
)
CASE = {"id": "t-1", "title": "Window", "method": "full", "text": TEXT,
        "options": {"a": "Mrs. Hale", "b": "Tom", "c": "Ann"}, "question": "Who broke the window?"}


def case_model():
    return {
        "case_id": "t-1",
        "people": [
            {"id": "P1", "name": "Mrs. Hale", "role": "neighbour", "statements": ["E1"]},
            {"id": "P2", "name": "Tom", "role": "gardener"},
            {"id": "P3", "name": "Ann", "role": "owner", "statements": ["E4"]},
        ],
        "evidence": [
            {"id": "E1", "kind": "testimony", "source": "Mrs. Hale", "quote": '"I was at the bakery until nine."',
             "reliability": "low", "shows": "claimed alibi", "does_not_show": "that she was near the window"},
            {"id": "E2", "kind": "observation", "source": "narrator", "quote": "The bakery closes at 8:30",
             "reliability": "high", "shows": "alibi is false", "does_not_show": "where she really was", "anomaly": True},
            {"id": "E3", "kind": "physical", "source": "narrator",
             "quote": "Tom's boots were caked in red clay ... under the broken window",
             "reliability": "high", "shows": "Tom stood by the window", "does_not_show": "that he broke it",
             "anomaly": True},
            {"id": "E4", "kind": "testimony", "source": "Ann", "quote": "Ann was on the phone with her sister",
             "reliability": "medium", "shows": "Ann's alibi", "does_not_show": "exact times"},
        ],
        "events": [{"id": "T1", "time": "evening", "description": "window broken", "people": ["P2"], "evidence": ["E3"]}],
        "contradictions": [{"id": "C1", "description": "bakery alibi vs closing time", "evidence": ["E1", "E2"], "implicates": ["P1"]}],
    }


def verdict(**overrides):
    v = {
        "case_id": "t-1", "method": "full", "answer": "b", "confidence": 0.7,
        "reasoning": "Clay places Tom at the window.",
        "key_evidence": [{"id": "E3", "quote": "caked in red clay", "why": "places him at the window"}],
        "hypotheses": [
            {"option": "a", "scenario": "s", "means": "m", "motive": "m", "opportunity": "lied about alibi",
             "supporting": ["E2"], "refuting": [], "unexplained": ["E3"], "status": "viable", "likelihood": 0.25},
            {"option": "b", "scenario": "s", "means": "m", "motive": "m", "opportunity": "o",
             "supporting": ["E3"], "refuting": [], "unexplained": ["E2"],
             "expected_missing": ["cuts or glass on Tom if he broke the pane: the text is silent, not denying"],
             "status": "leading", "likelihood": 0.7},
            {"option": "c", "scenario": "s", "means": "m", "motive": "m", "opportunity": "o",
             "supporting": [], "refuting": ["E4"], "status": "eliminated", "likelihood": 0.05},
        ],
        "challenges": [
            {"target": "b", "check": "attack", "attack": "clay proves presence, not guilt", "evidence": ["E3"],
             "survived": True, "resolution": "no one else has physical trace"},
            {"target": "b", "check": "anomaly", "attack": "Tom's guilt leaves Mrs. Hale's false alibi unexplained",
             "evidence": ["E1", "E2"], "survived": True,
             "resolution": "a false alibi shows a lie, not the window; nothing ties her to the garden"},
        ],
    }
    v.update(overrides)
    return v


@pytest.fixture
def case_dir(tmp_path):
    counter = iter(range(100))

    def make(case=CASE, cm=case_model(), v=None):
        d = tmp_path / f"case{next(counter)}"
        d.mkdir()
        (d / "case.json").write_text(json.dumps(case))
        if cm is not None:
            (d / "case_model.json").write_text(json.dumps(cm))
        (d / "verdict.json").write_text(json.dumps(v or verdict()))
        return d
    return make


def test_grounding_tolerates_typography_and_ellipsis():
    assert checks.is_grounded("\"I was at the bakery until nine.\"", TEXT)  # straight vs curly quotes
    assert checks.is_grounded("closes at 8:30 — every regular", TEXT)  # em dash vs --
    assert checks.is_grounded("Tom's boots … broken window", TEXT)
    assert not checks.is_grounded("broken window ... Tom's boots", TEXT)  # order matters
    assert not checks.is_grounded("Tom was seen at the window", TEXT)
    assert not checks.is_grounded("...", TEXT)


def test_valid_full_case_passes(case_dir):
    report = checks.validate(case_dir())
    assert report.ok, report.errors
    assert report.quotes == 5


def test_invented_quote_is_caught(case_dir):
    cm = case_model()
    cm["evidence"][2]["quote"] = "Tom admitted breaking the window"
    report = checks.validate(case_dir(cm=cm))
    assert report.ungrounded == ["case_model.E3"]


def test_dangling_ids_are_caught(case_dir):
    v = verdict(key_evidence=[{"id": "E9", "quote": "red clay", "why": "x"}])
    report = checks.validate(case_dir(v=v))
    assert any("E9" in d for d in report.dangling)


def test_reasoning_rules(case_dir):
    v = verdict()
    v["hypotheses"][2]["refuting"] = []
    assert any("eliminated without refuting" in e for e in checks.validate(case_dir(v=v)).errors)

    v = verdict(challenges=[])
    assert any("requires at least one challenge" in e for e in checks.validate(case_dir(v=v)).errors)

    v = verdict(hypotheses=verdict()["hypotheses"][:2])
    assert any("cover each option" in e for e in checks.validate(case_dir(v=v)).errors)

    v = verdict()
    v["hypotheses"][1]["unexplained"] = ["E4"]  # Ann's call is not flagged as an anomaly
    assert any("not anomaly evidence" in e for e in checks.validate(case_dir(v=v)).errors)

    v = verdict(answer="insufficient")
    errors = checks.validate(case_dir(v=v)).errors
    assert any("requires missing_evidence" in e for e in errors)


def test_baseline_needs_no_case_model(case_dir):
    v = {"case_id": "t-1", "method": "baseline", "answer": "a", "confidence": 0.5, "reasoning": "r",
         "key_evidence": [{"quote": "The bakery closes at 8:30", "why": "alibi broken"}]}
    assert checks.validate(case_dir(case={**CASE, "method": "baseline"}, cm=None, v=v)).ok
    # a baseline verdict submitted into a 'full' assignment is rejected
    assert any("assigned method" in e for e in checks.validate(case_dir(cm=None, v=v)).errors)


def test_score_uses_first_validation_for_hallucination(case_dir):
    cm = case_model()
    cm["evidence"][0]["quote"] = "I was home all night"
    d = case_dir(cm=cm)
    checks.validate(d)  # first attempt: one ungrounded quote
    (d / "case_model.json").write_text(json.dumps(case_model()))
    checks.validate(d)  # fixed
    puzzle = Puzzle("t-1", "Window", TEXT, CASE["options"], "b", "", 40.0, 100)
    s = score_case(d, puzzle)
    assert (s.correct, s.gate_ok, s.first_ungrounded, s.attempts) == (True, True, 1, 2)


def test_common_knowledge_is_counted_not_grounded(case_dir):
    cm = case_model()
    cm["evidence"].append({"id": "E5", "kind": "common_knowledge", "source": "baking trade",
                           "quote": "Bakeries rarely stay open past evening", "reliability": "medium",
                           "shows": "late alibi is unusual", "does_not_show": "this bakery's hours"})
    v = verdict(key_evidence=[
        {"id": "E5", "quote": "Bakeries rarely stay open past evening", "why": "x"},
        {"id": "E3", "quote": "caked in red clay", "why": "y"},
    ])
    report = checks.validate(case_dir(cm=cm, v=v))
    assert report.ok, report.errors
    assert report.knowledge == ["case_model.E5", "verdict.key_evidence[0]"]
    # the flag is required for baseline, which has no case model to carry the kind
    base = {"case_id": "t-1", "method": "baseline", "answer": "b", "confidence": 0.5, "reasoning": "r",
            "key_evidence": [{"quote": "Clay stains are hard to remove", "why": "w"}]}
    d = case_dir(case={**CASE, "method": "baseline"}, cm=None, v=base)
    assert checks.validate(d).ungrounded
    base["key_evidence"][0]["common_knowledge"] = True
    (d / "verdict.json").write_text(json.dumps(base))
    assert checks.validate(d).ok


def test_parse_options():
    assert parse_options("(a) Chris Henderson; (b) Dave Perkins; (c) Larry") == {
        "a": "Chris Henderson", "b": "Dave Perkins", "c": "Larry"}
    assert parse_options("(a) Bedroom of daughter; Anita; (b) Bath") == {"a": "Bedroom of daughter; Anita", "b": "Bath"}


def test_report_renders_validated_outputs(case_dir):
    from b221 import report
    text = report.render(case_dir())
    assert "(b) Tom" in text and "확신도 0.70" in text
    assert "⚠ **C1**" in text and "| (c) Ann | 제외 |" in text and "버팀" in text
    assert "공격 [설명 안 된 이상 사실]" in text and "있어야 하는데 없는 흔적" in text and "이상 사실]" in text
