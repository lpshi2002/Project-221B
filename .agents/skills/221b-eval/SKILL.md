---
name: 221b-eval
description: 221B 벤치마크 오케스트레이터. True Detective 추리 퍼즐로 탐정 방식(baseline / structured / full)을 실행하고 채점해 비교표를 만든다. "221B 평가 돌려줘", "기준선 점수 내줘", "반론 검사 효과 비교해줘", "N문제로 벤치마크", 결과 표·정답률·환각률을 요청하면 반드시 사용한다. 사건 하나를 직접 추리하는 요청은 221b-investigate를 쓴다.
---

# 221B 벤치마크 실행

너는 **감독**이다. 사건을 직접 풀지 않는다. 사건마다 새 컨텍스트의 탐정에게 배정하고, 검증 상태를 확인하고, 채점한다.
감독이 직접 풀면 앞 사건의 추론과 다른 방식의 풀이가 섞여 비교 실험이 오염된다.

## 1. 준비

```
uv run b221 fetch                      # data/가 없을 때만
uv run b221 prepare --method baseline --n 10 --seed 0 --run <이름>-baseline
uv run b221 prepare --method full     --n 10 --seed 0 --run <이름>-full
```

- 방식끼리 비교할 때는 **같은 seed**로 같은 사건 집합을 쓴다.
- 쉬운 문제에서 방식 차이가 안 보이면(천장 효과) `--hardest`로 사람 정답률이 가장 낮은 N문제를 쓴다.
- 요청에 문제 수가 없으면 10문제, 방식이 없으면 baseline과 full을 비교한다.
- 감독도 `data/`와 정답을 열지 않는다. 채점은 `b221 score`가 한다.

## 2. 배정

사건 폴더 하나 = 탐정 하나 = 새 컨텍스트. 한 탐정에게 같은 사건의 다른 방식을 맡기지 않는다.

**Claude Code:** Agent 도구로 `221b-detective` 서브에이전트를 띄운다(정의: `.claude/agents/221b-detective.md`). 목록에 없으면 `general-purpose`로 띄우고 첫 줄에 "`.claude/agents/221b-detective.md`를 읽고 그 지시를 따르라"고 쓴다. 백그라운드로 한 번에 5개 이하.

**Codex:** `221b_detective` 에이전트(정의: `.codex/agents/221b-detective.toml`)를 사건마다 띄운다. 서브에이전트를 쓸 수 없는 환경이면 한 세션에서 순서대로 풀되, **한 세션에서는 한 방식만** 실행하고 결과 파일에 "단일 세션 실행"이라고 적는다.

배정 메시지 형식(정답이나 다른 사건 정보를 넣지 않는다):

```
사건 폴더: runs/<run>/<case-id>
221b-investigate 절차로 풀고 게이트를 통과시켜라. 사건 폴더 밖은 읽지 마라.
```

## 3. 확인과 재시도

탐정이 모두 끝나면 사건마다 기록을 남기지 않는 검증으로 상태를 확인한다:

```
uv run b221 validate runs/<run>/<case-id> --no-log
```

- FAIL이거나 `verdict.json`이 없는 사건은 새 탐정에게 **한 번만** 다시 배정한다(기존 폴더 그대로, 이어서 고치게).
- 재시도도 실패하면 그대로 둔다. 채점표에 `gate FAIL`로 드러난다. 감독이 결과 파일을 고치지 않는다.

## 4. 채점과 보고

```
uv run b221 score runs/<run-a> runs/<run-b> --out results/<YYYY-MM-DD>-<이름>.md
```

생성된 파일 아래에 `## 해석`을 덧붙인다:
- 방식별 정답률 차이와 표본 크기(10문제면 1문제 = 10%p, 차이가 우연일 수 있음을 적는다)
- 첫 시도 인용 불일치율(환각 지표)과 게이트 통과율
- 확신도 보정(Brier, 낮을수록 좋음), 사람 평균 정답률 대비
- full 방식이면 사건별 `verdict.json`의 `challenges[].check`와 `survived`를 보고, 어느 검사(진단력, 제외 검사 등)가 결론을 바꿨는지 적는다
- 틀린 사건 몇 개는 `report.md`와 정답을 대조해 **왜** 틀렸는지 한 줄씩(이때는 채점이 끝났으니 정답을 봐도 된다: `uv run python -c "from b221.dataset import by_id; p=by_id()['td-XXX']; print(p.answer, p.outcome)"`)
- 실행 환경(도구, 모델, 단일 세션 여부)과 한계(원작이 학습 데이터에 있을 가능성 등)

`results/`는 커밋 대상이다. `runs/`와 `data/`는 저작권 때문에 커밋하지 않는다.

## 테스트 시나리오

- **정상:** `prepare`(2개 방식 × 3문제) → 탐정 6명 → 모두 PASS → `score`가 두 방식 표를 출력.
- **게이트 실패:** 탐정 하나가 원문에 없는 인용을 씀 → 첫 validate FAIL(로그에 기록) → 탐정이 고쳐 PASS → 채점표의 "1st-pass ungrounded"에 반영되고 `validations`가 2 이상.
- **탐정 무응답:** `verdict.json` 없음 → 1회 재배정 → 그래도 없으면 채점표에 `-`/`FAIL`로 남김.
