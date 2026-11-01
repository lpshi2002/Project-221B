"""Case model and verdict schema (prototype-221B.md §4).

ID conventions: people P1.., evidence E1.., events T1.., contradictions C1...
Every ``quote`` must be a verbatim excerpt of the case text; ``...`` may join
non-adjacent fragments. ``b221 validate`` enforces both rules. The one exception
is ``common_knowledge``: a general fact the puzzle expects the reader to bring
(historical dates, how ducks behave). It is not grounded in the text, so the
gate counts it separately instead of accepting it silently.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Reliability = Literal["high", "medium", "low"]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Evidence(_Strict):
    id: str = Field(pattern=r"^E\d+$")
    kind: Literal["physical", "biological", "digital", "testimony", "observation", "document", "common_knowledge"]
    source: str = Field(description="Who or what provides this (narrator, a suspect, a record...); "
                        "for common_knowledge, the field of knowledge")
    quote: str = Field(min_length=1, description="Verbatim excerpt from the case text; "
                       "for common_knowledge, the general fact relied on")
    time: str | None = Field(None, description="Point or range, as precise as the text allows")
    reliability: Reliability
    shows: str = Field(description="What this evidence tells us")
    does_not_show: str = Field(description="What it does NOT establish — guards against over-reading")
    anomaly: bool = Field(False, description="A surprising fact that ordinary events don't explain; "
                          "every hypothesis is judged on which anomalies it explains")


class Person(_Strict):
    id: str = Field(pattern=r"^P\d+$")
    name: str
    role: str = Field(description="Relationship to the case / victim")
    statements: list[str] = Field(default_factory=list, description="Evidence IDs of their testimony")
    motives: list[str] = Field(default_factory=list, description="Candidate motives, each backed in evidence")


class Event(_Strict):
    id: str = Field(pattern=r"^T\d+$")
    time: str = Field(description="Clock time, range, or relative anchor ('before the accident')")
    description: str
    place: str | None = None
    people: list[str] = Field(default_factory=list, description="Person IDs")
    evidence: list[str] = Field(min_length=1, description="Evidence IDs that establish this event")


class Contradiction(_Strict):
    id: str = Field(pattern=r"^C\d+$")
    description: str
    evidence: list[str] = Field(min_length=2, description="The evidence items that conflict")
    implicates: list[str] = Field(default_factory=list, description="Person IDs whose account breaks")


class CaseModel(_Strict):
    case_id: str
    people: list[Person]
    evidence: list[Evidence] = Field(min_length=1)
    events: list[Event] = Field(default_factory=list)
    contradictions: list[Contradiction] = Field(default_factory=list)


class Hypothesis(_Strict):
    option: str = Field(pattern=r"^[a-z]$")
    scenario: str
    means: str
    motive: str
    opportunity: str
    supporting: list[str] = Field(default_factory=list, description="Evidence IDs")
    refuting: list[str] = Field(default_factory=list, description="Evidence IDs")
    unexplained: list[str] = Field(default_factory=list, description="IDs of anomaly evidence this hypothesis leaves unexplained")
    expected_missing: list[str] = Field(default_factory=list, description="Traces this hypothesis predicts but the text lacks "
                                        "(say whether the text denies them or is silent)")
    status: Literal["eliminated", "viable", "leading"]
    likelihood: float = Field(ge=0, le=1)


Check = Literal["attack", "attribution", "exclusion", "exempted", "witness", "runner_up",
                "diagnosticity", "assumption", "linchpin", "anomaly", "absence"]


class Challenge(_Strict):
    target: str = Field(pattern=r"^[a-z]$", description="Option the skeptic attacked")
    check: Check | None = Field(None, description="Which step-4 check produced this challenge")
    attack: str
    evidence: list[str] = Field(default_factory=list)
    survived: bool = Field(description="True if the target hypothesis withstood this attack")
    resolution: str


class KeyEvidence(_Strict):
    id: str | None = Field(None, description="Evidence ID when a case model exists")
    quote: str = Field(min_length=1, description="Verbatim excerpt from the case text, or the general fact if common_knowledge")
    common_knowledge: bool = Field(False, description="True if this is outside knowledge, not a case-text excerpt")
    why: str = Field(description="How this excerpt supports the answer")


class Verdict(_Strict):
    case_id: str
    method: Literal["baseline", "structured", "full"]
    answer: str = Field(pattern=r"^([a-z]|insufficient)$")
    confidence: float = Field(ge=0, le=1)
    reasoning: str
    key_evidence: list[KeyEvidence] = Field(min_length=1)
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    challenges: list[Challenge] = Field(default_factory=list)
    speculation: list[str] = Field(default_factory=list, description="Claims not backed by evidence, labelled as such")
    missing_evidence: list[str] = Field(default_factory=list, description="What would settle it (required if insufficient)")
