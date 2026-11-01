# 작은 완성 예시 (method: full)

형식을 보여 주는 예시다. 실제 사건은 훨씬 길고 증거도 많다. 이 예시는 `tests/test_checks.py`의 픽스처와 같으며 게이트를 통과한다.

## case.json (발췌)

```json
{
  "id": "t-1",
  "method": "full",
  "options": {
    "a": "Mrs. Hale",
    "b": "Tom",
    "c": "Ann"
  },
  "text": "Mrs. Hale said, “I was at the bakery until nine.” The bakery closes at 8:30 -- every regular knows that. Tom's boots were caked in red clay, the same clay as the garden bed under the broken window. Ann was on the phone with her sister all evening."
}
```

## case_model.json

```json
{
  "case_id": "t-1",
  "people": [
    {
      "id": "P1",
      "name": "Mrs. Hale",
      "role": "neighbour",
      "statements": [
        "E1"
      ]
    },
    {
      "id": "P2",
      "name": "Tom",
      "role": "gardener"
    },
    {
      "id": "P3",
      "name": "Ann",
      "role": "owner",
      "statements": [
        "E4"
      ]
    }
  ],
  "evidence": [
    {
      "id": "E1",
      "kind": "testimony",
      "source": "Mrs. Hale",
      "quote": "\"I was at the bakery until nine.\"",
      "reliability": "low",
      "shows": "claimed alibi",
      "does_not_show": "that she was near the window"
    },
    {
      "id": "E2",
      "kind": "observation",
      "source": "narrator",
      "quote": "The bakery closes at 8:30",
      "reliability": "high",
      "shows": "alibi is false",
      "does_not_show": "where she really was",
      "anomaly": true
    },
    {
      "id": "E3",
      "kind": "physical",
      "source": "narrator",
      "quote": "Tom's boots were caked in red clay ... under the broken window",
      "reliability": "high",
      "shows": "Tom stood by the window",
      "does_not_show": "that he broke it",
      "anomaly": true
    },
    {
      "id": "E4",
      "kind": "testimony",
      "source": "Ann",
      "quote": "Ann was on the phone with her sister",
      "reliability": "medium",
      "shows": "Ann's alibi",
      "does_not_show": "exact times"
    }
  ],
  "events": [
    {
      "id": "T1",
      "time": "evening",
      "description": "window broken",
      "people": [
        "P2"
      ],
      "evidence": [
        "E3"
      ]
    }
  ],
  "contradictions": [
    {
      "id": "C1",
      "description": "bakery alibi vs closing time",
      "evidence": [
        "E1",
        "E2"
      ],
      "implicates": [
        "P1"
      ]
    }
  ]
}
```

## verdict.json

```json
{
  "case_id": "t-1",
  "method": "full",
  "answer": "b",
  "confidence": 0.7,
  "reasoning": "Clay places Tom at the window.",
  "key_evidence": [
    {
      "id": "E3",
      "quote": "caked in red clay",
      "why": "places him at the window"
    }
  ],
  "hypotheses": [
    {
      "option": "a",
      "scenario": "s",
      "means": "m",
      "motive": "m",
      "opportunity": "lied about alibi",
      "supporting": [
        "E2"
      ],
      "refuting": [],
      "unexplained": [
        "E3"
      ],
      "status": "viable",
      "likelihood": 0.25
    },
    {
      "option": "b",
      "scenario": "s",
      "means": "m",
      "motive": "m",
      "opportunity": "o",
      "supporting": [
        "E3"
      ],
      "refuting": [],
      "unexplained": [
        "E2"
      ],
      "expected_missing": [
        "cuts or glass on Tom if he broke the pane: the text is silent, not denying"
      ],
      "status": "leading",
      "likelihood": 0.7
    },
    {
      "option": "c",
      "scenario": "s",
      "means": "m",
      "motive": "m",
      "opportunity": "o",
      "supporting": [],
      "refuting": [
        "E4"
      ],
      "status": "eliminated",
      "likelihood": 0.05
    }
  ],
  "challenges": [
    {
      "target": "b",
      "check": "attack",
      "attack": "clay proves presence, not guilt",
      "evidence": [
        "E3"
      ],
      "survived": true,
      "resolution": "no one else has physical trace"
    },
    {
      "target": "b",
      "check": "anomaly",
      "attack": "Tom's guilt leaves Mrs. Hale's false alibi unexplained",
      "evidence": [
        "E1",
        "E2"
      ],
      "survived": true,
      "resolution": "a false alibi shows a lie, not the window; nothing ties her to the garden"
    }
  ]
}
```

## 짚어 볼 점

- E3 인용은 `...`로 떨어진 두 구절을 이었다. 순서가 원문과 같아야 한다.
- E1의 `does_not_show`처럼 증거가 **증명하지 않는 것**을 적어 두면, 거짓 알리바이(C1)를 곧바로 범행 증거로 오독하지 않게 된다. 그래서 (a)는 `eliminated`가 아니라 `viable`이다.
- (c)는 반대 증거(E4)가 있으므로 `eliminated`를 쓸 수 있다.
- 반론 검사는 "진흙은 현장에 있었다는 것만 보여 준다"로 유력 가설을 공격했고, 다른 용의자에게는 물리적 흔적이 없어 가설이 버텼다.
- E2(문 닫은 빵집)와 E3(창 밑 진흙)은 평범한 경위로 설명되지 않는 **이상 사실**이라 `anomaly: true`다. 가설마다 설명하지 못하는 이상 사실을 `unexplained`에 적는다. (a)는 진흙을, (b)는 거짓 알리바이를 설명하지 못한다.
- 유력 가설 (b)가 남긴 이상 사실(E2)은 `check: "anomaly"` 반론으로 따로 공격했다. 거짓 알리바이는 거짓말을 보여 줄 뿐 창문과 이어지지 않아 가설이 버텼다.
- `expected_missing`에는 원문이 그 흔적을 **부정**하는지 **언급하지 않는지**를 구분해 적는다. 언급이 없는 것은 약한 반대 근거다.
