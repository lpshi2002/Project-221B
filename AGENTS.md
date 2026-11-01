# 221B — 추리 탐정 AI 하네스

개념과 로드맵은 `prototype-221B.md`. 이 저장소는 그 축소판(1~3단계)을 **Claude Code / Codex에서 실행하는 하네스**로 구현한다.
추리는 에이전트가 하고, `b221` CLI(`src/b221/`)는 사건 준비·검증·채점만 한다.

## 구성

| 경로 | 역할 |
|---|---|
| `.agents/skills/221b-investigate/` | 사건 1건 추리 절차 (정리 → 교차 검증 → 가설 → 반증 → 결론 → 게이트 → 보고서) |
| `.agents/skills/221b-eval/` | 벤치마크 오케스트레이터 (사건마다 새 탐정 배정 → 확인 → 채점) |
| `.claude/skills` | `.agents/skills`로 가는 심볼릭 링크 (Claude Code용) |
| `.claude/agents/221b-detective.md`, `.codex/agents/221b-detective.toml` | 사건 하나를 푸는 탐정 에이전트 (두 도구용, 내용 동일) |
| `harness/` | 복잡도 판단과 완료 기준 |
| `docs/investigative-methods.md` | 추리·수사 방법론 정리와 탐정 스킬 반영 상태 (사람이 읽는 용도) |
| `results/` | 채점 결과 (커밋 대상) |

## 명령

```
uv sync                                   # 의존성 (pydantic, pytest)
uv run pytest -q                          # 검증기·채점 테스트
uv run b221 fetch                         # True Detective 데이터 → data/
uv run b221 prepare --method full --n 10 --seed 0     # --hardest: 사람 정답률 최하위 N문제
uv run b221 validate runs/<run>/<case-id>
uv run b221 report runs/<run>/<case-id>     # verdict → report.md
uv run b221 score runs/<run-a> runs/<run-b> --out results/<파일>.md
uv run b221 new <이름> --text story.txt --suspects "A; B; C"   # 직접 만든 사건
```

Codex 샌드박스에서 uv 캐시 쓰기가 막히면: `UV_CACHE_DIR=/tmp/uv-cache uv run --offline b221 ...` (먼저 `uv sync`가 되어 있어야 한다).

## 규칙

- `data/`, `runs/`는 커밋하지 않는다. True Detective는 학술 연구용으로만 쓸 수 있다.
- 사건을 푸는 에이전트는 자기 사건 폴더 밖(`data/`, 다른 `runs/`, `results/`)을 읽지 않는다. 정답이 새면 평가가 무효가 된다.
- 실존 인물이나 진행 중인 실제 사건에는 쓰지 않는다(명예훼손·2차 피해). 추리 퍼즐, 소설, 판결이 끝난 공개 사례로 한정한다.
- 검증 기준(`src/b221/checks.py`)을 통과시키려고 약화하지 않는다. 바꿀 때는 테스트를 함께 고친다.
