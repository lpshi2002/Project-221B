# 추리·수사 방법론 정리

221B가 쓰는(또는 쓸) 추리·수사 방법을 한곳에 모은 문서다. 사람이 읽고 배우는 용도이고, 탐정 에이전트가 실제로 따르는 절차는 `.agents/skills/221b-investigate/SKILL.md`에 있다.

> 2026-11 작성. 출처는 각 항목의 번호로 맨 아래에 모았다. 링크가 있는 것은 검색으로 확인했고, 링크가 없는 것은 널리 인용되는 고전 문헌이라 서지 정보만 적었다.

## 읽는 법

방법론은 하는 일에 따라 일곱 묶음으로 나뉜다.

1. **태도와 편향 관리:** 틀린 결론에 갇히지 않는 법
2. **증거 평가:** 증거 하나가 무엇을 얼마나 말해 주는가
3. **교차 검증:** 사실끼리 맞춰 보기
4. **가설 만들기:** 무슨 일이 있었는지 후보 이야기 세우기
5. **가설 시험:** 후보를 무너뜨려 보기
6. **결론:** 무엇을 고르고 얼마나 확신하는가
7. **다음 수사:** 무엇을 더 확인해야 하는가

각 항목의 **221B** 칸은 현재 반영 상태다.

| 표기 | 뜻 |
|---|---|
| **v2** | 이전부터 탐정 스킬에 있던 것 |
| **v3** | 2026-11에 추가한 것 (아직 검증 전) |
| **Phase A·B** | 지금 입력(이야기 텍스트 한 편)으로는 할 수 없거나, 코드·모듈이 더 필요한 것 |
| **제외** | 일부러 쓰지 않는 것 |

---

## 1. 태도와 편향 관리

수사 실패의 가장 흔한 원인은 지식 부족이 아니라 **너무 일찍 한 사람을 정하고 거기에 맞는 증거만 보는 것**이다. 이를 터널 비전이라 부른다. 오판 사례 연구에서 반복해서 나온다[2].

| 방법 | 핵심 질문 | 예 | 221B |
|---|---|---|---|
| **ABC 원칙**[1] | 아무것도 가정하지 않고, 아무것도 그냥 믿지 않고, 모든 것을 따져 봤나? | "가정부가 9시에 나갔다고 했다" → 다른 기록으로 확인되나? | v2: 원칙 전반 |
| **다수 의견 함정**[1] | 한 사람만 다르게 말할 때, 그 한 사람을 무시하고 있지 않나? | 목격자 넷은 빨간 차, 한 명은 파란 차 → 그 불일치 자체를 조사한다 | v2: 모순 기록 |
| **터널 비전 경계**[2] | 첫 용의자 말고 다른 사람도 같은 기준으로 봤나? | 신고자를 처음부터 피해자 편으로 놓고 의심하지 않음 | v2: 모든 선택지에 가설 / v3: **판단은 늦게** |
| **순차적 정보 공개 (LSU, LSU-E)**[3][4] | 용의자 정보를 보기 전에 증거부터 판단했나? | 감식관이 용의자 지문을 보기 전에 현장 지문의 특징부터 기록한다 | v3: ①②에서 판단 보류. 탐정이 이야기를 통째로 읽으므로 완전한 적용은 불가하다. Phase A에서 자료를 단계별로 공개하는 실험이 가능하다 |

## 2. 증거 평가

증거 하나를 볼 때 묻는 것은 세 가지다.
- **누가 말했나:** 출처
- **맞는 말인가:** 내용
- **무엇을 증명하나:** 범위

| 방법 | 핵심 질문 | 예 | 221B |
|---|---|---|---|
| **보여 주는 것 / 보여 주지 않는 것** | 이 증거가 증명하지 **않는** 것은 무엇인가? | 장화의 진흙 → 창 밑에 있었다(O), 창을 깼다(X) | v2: `shows` / `does_not_show` |
| **출처와 내용을 따로 평가**[5] | 출처는 믿을 만한가? 내용은 다른 증거와 맞나? 둘은 별개다 | 늘 정직한 사람도 잘못 볼 수 있고, 거짓말쟁이도 사실을 말할 수 있다 | v3: 지침. 스키마는 아직 `reliability` 한 칸이고, Phase A 증거 모델 v2에서 두 칸으로 나눈다 |
| **목격 조건 점검 (ADVOKATE)**[6] | 얼마나 오래, 얼마나 멀리서, 얼마나 밝을 때, 가린 것 없이 봤나? 아는 사람이었나? 기억할 이유가 있었나? 시간이 얼마나 지났나? 처음 묘사와 실제가 다른가? | "어두운 골목 30m 밖에서 2초 봤다" → 신원 확인의 근거로 약하다 | v3: ① 신뢰도 판단 |
| **증거 수준 계층**[7] | 이 증거는 출처(누구의 것), 행위(무엇을 했나), 범행(죄를 지었나) 중 어디까지 말하나? | 현장의 DNA가 A의 것이다(출처) ≠ A가 그날 그 방에서 다퉜다(행위) ≠ A가 죽였다(범행) | 일부: `does_not_show`. Phase B 감식 모듈에서 명시적으로 다룬다 |
| **진단력**[8] | 이 증거는 경쟁 가설이 맞아도 똑같이 나올까? | "범인은 오른손잡이" → 용의자 넷이 다 오른손잡이면 가르는 힘이 0이다 | v3: ④-6 **진단력 검사** |
| **가능도 비와 검사의 오류**[7][8] | "무죄라면 이 증거가 나올 확률"과 "이 증거가 있을 때 무죄일 확률"을 헷갈리지 않았나? | "무작위 일치 확률 100만분의 1"은 "무죄일 확률 100만분의 1"이 아니다. 도시 인구가 천만이면 일치하는 사람이 10명쯤 있다 | 개념은 v3 진단력 검사에 반영. 숫자로 합산하는 것은 Phase B(LEAP 방식) |
| **이상 사실**[9] | 평범한 경위로는 설명되지 않는 사실은 무엇인가? | 문 닫은 빵집에 있었다는 알리바이, 맑은 날 젖은 우산 | v3: `anomaly` 표시 |

**이상 사실이 출발점인 이유.** 가추 추론(관찰을 가장 잘 설명하는 가설을 찾는 추론)의 기본형은 이렇다[9].
1. 놀라운 사실 C가 관찰된다.
2. A가 참이라면 C는 당연한 일이 된다.
3. 그러므로 A가 참이라고 의심할 이유가 있다.

평범한 사실은 어느 가설로도 설명되므로 가설을 가르지 못한다. 범인을 가르는 것은 이상 사실이다.

## 3. 교차 검증

증거를 한 줄로 세워 서로 부딪히는 곳을 찾는 단계다.

| 방법 | 핵심 질문 | 예 | 221B |
|---|---|---|---|
| **타임라인·동선 겹치기** | 각 인물이 언제 어디 있었나? 같은 시각에 두 곳에 있다는 기록이 있나? | 9시에 극장에 있었다는 사람이 9시 5분 편의점 CCTV에 찍힘 | v2 |
| **시간·거리 가능성, 알리바이 공백** | t1에 A, t2에 B가 이동 가능한가? 범행 시간창 중 기록으로 덮이지 않는 구간은? | 20km를 10분에 → 시속 120km가 필요하다 | v3: 계산은 코드로. 엔진은 Phase A |
| **진술 모순·진술 변화** | 진술끼리, 같은 사람의 앞뒤 진술끼리 맞나? | 처음엔 "혼자 있었다", 나중엔 "친구와 있었다" | v2 |
| **범인만 아는 정보**[10] | 이 사람은 이 사실을 알 수 있었나? 경찰이 공개하지 않은 사실을 먼저 말했나? | "독살됐다"는 발표 전에 "독이라니"라고 말함 | v2: 모순 유형 / v3: 정보 노출 확인. 정보 노출 타임라인 구조는 Phase B 진술 모듈 |
| **발언 귀속** | 이 말은 말한 사람의 생각인가, 남의 말을 옮긴 것인가? | "그가 범인이래"는 말한 사람이 아니라 전해 준 사람의 판단이다 | v2 |
| **물리·상식·시대 대조**[11] | 물리 법칙, 날씨·일몰, 물질 상태, 무기와 상처, 시대 배경과 맞나? 접촉했다면 흔적이 남았을 텐데 있나?(로카르 교환 원칙) | 산탄총이라면서 상처는 단발 총상 / 기원전 동전에 "B.C." 각인 | v3: ② 점검표. 감식 모듈은 Phase B |
| **현장 재구성**[12] | 물리적 흔적으로 사건의 순서를 정할 수 있나? | 핏자국 위에 발자국 → 피가 흐른 뒤에 누군가 걸어감 | 일부(텍스트 범위). Phase B·C |

## 4. 가설 만들기

| 방법 | 핵심 질문 | 예 | 221B |
|---|---|---|---|
| **육하원칙 (5W1H)** | 누가, 무엇을, 언제, 어디서, 왜, 어떻게? | — | v2: ①② 정리 칸 |
| **수단·동기·기회 (MMO), 알리바이를 더한 MOMA**[13] | 할 수 있었나(수단), 할 이유가 있었나(동기), 그때 그곳에 있을 수 있었나(기회), 없었다는 증명이 있나(알리바이)? | — | v2: 가설마다 수단·동기·기회 |
| **최선의 설명 추론**[9][14] | 어느 가설이 증거, 특히 이상 사실을 가장 많이, 가장 적은 추가 가정으로 설명하나? | — | v3: `unexplained`에 가설이 설명 못 하는 이상 사실 기록 |
| **경쟁 시나리오 (이야기 + 논증)**[15][16] | 각 가설을 "무슨 일이 있었나"라는 완결된 이야기로 쓸 수 있나? 그 이야기의 고리마다 증거나 믿을 만한 상식이 받치고 있나? | — | v2: `scenario` 칸 / v3: 핵심 가정 점검 |
| **정박된 이야기 (anchored narratives)**[16] | 이야기의 각 고리가 무엇에 "정박"돼 있나? 그 정박점(상식 일반화)은 정말 안전한가? | "도망친 사람은 죄가 있다"는 정박점은 안전하지 않다. 겁이 나서 도망칠 수도 있다 | v3: 핵심 가정 점검으로 일부 반영 |
| **연출·누명 탐지**[17][18] | 현장이 누군가 꾸민 것일 수 있나? 꾸민 사람이 일부러 남길 흔적은 무엇인가? | 가짜 침입 흔적이 있는데 침입 경로가 없다, 귀중품은 두고 사소한 물건만 없어졌다, 상처가 주장한 경위와 맞지 않는다, 무기 배치가 너무 완벽하다, 신고자·발견자가 연출자다 | v3: ③ 연출·누명 시나리오 + ④-6 진단력 검사 |

## 5. 가설 시험

좋은 수사관은 자기 가설이 **맞다는 증거를 찾지 않고 틀렸다는 증거를 찾는다.** 맞다는 증거는 틀린 가설에서도 쉽게 모이기 때문이다.

**경쟁 가설 분석 (ACH)**[8]은 CIA 분석관 Heuer가 만든 8단계 절차다. 221B 반영 상태를 단계별로 대응시키면 다음과 같다.

| ACH 단계 | 내용 | 221B |
|---|---|---|
| 1 | 가능한 가설을 모두 나열 | v2: 모든 선택지 |
| 2 | 증거와 가정, **증거의 부재**까지 나열 | v2: 증거 / v3: `expected_missing` |
| 3 | 증거 × 가설 행렬을 만들고 부합·모순 표시 | 일부: 가설마다 지지·반대 목록. 전체 행렬은 아님 |
| 4 | 모든 가설과 똑같이 맞는 증거(진단력 없음)를 걸러냄 | v3: ④-6 진단력 검사 |
| 5 | 잠정 결론을 내고, 맞는 가설이 아니라 **반증하려는** 쪽으로 검토 | v2: ④ 반증 |
| 6 | 결론이 기대는 핵심 증거가 틀리면 어떻게 되나(민감도) | v3: ④-8 핵심 증거 민감도 |
| 7 | 1위만이 아니라 모든 가설의 상대적 가능성을 보고 | v2: `likelihood` |
| 8 | 판단을 바꿀 미래의 지표 제시 | v3: `missing_evidence` 상시 작성 |

그 밖의 시험 방법:

| 방법 | 핵심 질문 | 예 | 221B |
|---|---|---|---|
| **예측 도출: 짖지 않은 개**[19] | 이 가설이 맞다면 무엇이 **있어야** 하나? 그것이 없나? | 셜록 홈즈 『실버 블레이즈』: 밤에 개가 짖지 않았다 → 범인은 개가 아는 사람이다 | v3: `expected_missing` + `absence` 반론 |
| **제외 검사 (불가능 vs 어려움)** | 이 사람을 뺀 근거가 정말 "할 수 없다"를 증명하나, 아니면 "하기 어렵다"만 보여 주나? | "글을 못 읽는다"는 어려움이다. 순서를 외워서 고를 수 있다(td-036) | v2 (실패 분석에서 나온 규칙) |
| **핵심 가정 점검**[20] | 결론이 증거 없이 기대고 있는 가정은? 그게 틀리면? | 시계가 맞다, 진술자가 직접 봤다, 단독범이다 | v3: ④-7 |
| **악마의 변호인, 레드팀, 사전 부검(premortem)**[21] | 이 결론이 틀렸다고 가정하면 가장 그럴듯한 이유는? | — | v2: 2위 가설 재건. 독립 반론 에이전트는 Phase B |
| **면제된 사람 점검** | 신고자, 피해자, 질문자, 조력자를 역할 때문에 의심에서 빼지 않았나? | 책 주인이자 질문자가 범인(td-163) | v2 |
| **목격자 시선으로 기회 검증** | 범행 순간 누가 보고 있었나? 들키지 않고 할 수 있었나? | 가게 앞을 지키던 사람이 있어서 기회가 없었다(td-163) | v2 |

## 6. 결론

| 방법 | 핵심 질문 | 221B |
|---|---|---|
| **이야기 모델의 확신 기준**[22] | 포괄성(증거를 얼마나 설명하나), 정합성(이야기 안에서 맞고 그럴 법하고 빠진 고리가 없나), 유일성(그만큼 잘 설명하는 다른 이야기가 없나) | v3: ⑤ 선택 기준. 유일성이 낮으면 확신도를 낮춘다 |
| **조건이 많을수록 확률은 낮아진다** | 이야기에 "그리고"가 붙을 때마다 전체 확률은 곱해서 줄어든다. 길고 자세한 이야기가 더 그럴듯해 보이는 착각(결합 오류)을 경계한다 | 정합성 기준에 일부 반영 |
| **확신도 보정** | 확신도 0.8이라고 말한 사건은 실제로 10번 중 8번 맞나? | v2: Brier로 측정. 증거별 가능도를 코드로 합산하는 것은 Phase B |
| **증거 부족 판단** | 증거가 선택지를 가려내지 못하면 지목하지 않는다 | v2: `insufficient` |

## 7. 다음 수사

| 방법 | 핵심 질문 | 221B |
|---|---|---|
| **정보 이득이 큰 확인**[23] | 상위 두 가설을 가장 크게 가를 미확보 사실은 무엇인가? | v3: `missing_evidence` 상시 작성. 채점은 Phase B. 모델은 스스로 고른 질문에 맞춰 가설을 세우는 경향이 있으므로 그대로 믿지 않는다[24] |

## 8. 자료가 더 있어야 쓰는 방법 (Phase A 이후)

지금 입력(이야기 한 편 + 선택지)에는 해당 자료가 없어서 쓸 수 없는 방법들이다.

| 방법 | 하는 일 | 필요한 자료 |
|---|---|---|
| 관계망(링크) 분석 | 사람·전화·계좌·장소를 그래프로 놓고 중심 인물, 숨은 연결을 찾는다 | 통화·메시지·금융 기록 |
| 자금 추적 | 돈의 흐름으로 동기와 공범을 찾는다 | 계좌·카드 내역 |
| 통신·위치 분석 | 기지국과 결제 위치로 동선을 복원하고 진술과 대조한다 | 기지국·결제·교통카드 |
| 디지털 포렌식 타임라인 | 기기 기록으로 분 단위 행동을 복원한다 | 휴대폰·PC 추출 자료 |
| 수법(MO)과 서명 구분, 연관 사건 분석 | 범행에 꼭 필요한 행동(수법)과 범인의 심리적 필요에서 나온 행동(서명)을 구분해 사건끼리 잇는다 | 여러 사건 기록 |
| 지리적 프로파일링 | 연쇄 사건 위치로 범인의 거주 지역을 추정한다 | 연쇄 사건 위치 |
| 피해자학 | 피해자의 생활·관계에서 범인과의 접점을 찾는다 | 피해자 주변 자료 |
| 신문 기법 (PEACE 모델, 증거의 전략적 사용 SUE, 인지 면담) | 사람에게 질문해 정보를 얻는다 | 221B는 기록만 읽으므로 직접 해당 없음. SUE의 핵심(진술과 증거의 불일치)은 ② 모순 검사로 반영 |

## 9. 일부러 쓰지 않는 것

| 방법 | 쓰지 않는 이유 |
|---|---|
| **SCAN** (진술 문장의 대명사·시제 변화로 거짓말 판별) | 참·거짓 진술을 구분하지 못한다는 연구가 반복됐다[25]. 경찰에서 쓰이지만 근거가 없다 |
| **CBCA, Reality Monitoring** (진술 내용의 풍부함으로 진실성 판단) | 대부분의 기준이 참·거짓을 통계적으로 구분했지만, 효과가 작고 상황에 따라 달라진다[26]. 결론의 근거로 쓰지 않고 참고만 한다 |
| **비언어 단서** (시선 회피, 얼굴 붉힘, 머뭇거림) | 거짓말 단서로서 대부분 약하다[27]. 실제로 td-137에서 baseline 탐정이 "지적당하자 얼굴을 붉혔다"는 미끼에 걸려 틀렸다 |
| **증거가 아닌 특성** (인종, 국적, 종교, 성별, 전과) | 편향을 만든다. 실사용 설계 원칙 13-3의 7번 |
| **추리 장르 관습** ("가장 의외의 인물이 범인", 공정 플레이 규칙) | 퍼즐 점수는 오를 수 있지만 실제 사건에는 맞지 않는다. 쓰더라도 기본값이 아닌 비교 실험용으로만 둔다 |

---

## v3에서 바뀐 것과 검증 계획

탐정 스킬(`SKILL.md`)과 스키마에 다음을 추가했다.
- 질문 유형 확인
- 판단은 늦게
- 계산은 코드로
- 출처·내용 분리와 목격 조건
- 이상 사실 표시(`anomaly`)
- 정보 노출·시간 거리·물리 상식 대조
- 가설별 설명 못 한 이상 사실(`unexplained`)과 있어야 할 흔적(`expected_missing`)
- 연출·누명 시나리오
- 진단력·핵심 가정·핵심 증거 민감도 검사
- 이야기 모델 선택 기준
- 반론마다 어느 검사에서 나왔는지(`check`)

검증 방법:
1. **새 홀드아웃**(`--hardest --skip 20`, 사람 정답률 하위 21–30위)에서 v2와 v3를 비교한다.
2. **무작위 10문제를 다시 돌려**, 규칙이 늘어나 맞던 답을 의심하다 틀리는 과교정이 없는지 본다.
3. `challenges[].check`로 **어느 검사가 결론을 바꿨는지** 사건별로 추적한다.
4. 사건당 토큰 증가를 기록한다.

10문제로는 규칙별 효과를 확정할 수 없다. 자동 러너와 MuSR이 생긴 뒤 표본을 늘려 확정한다.

## 출처

1. College of Policing, [Investigation process](https://www.college.police.uk/app/investigation/investigation-process); [Conducting effective investigations guidelines (2022)](https://assets.college.police.uk/s3fs-public/2022-07/Conducting-effective-investigations-guidelines.pdf)
2. Findley, K. & Scott, M. (2006). The Multiple Dimensions of Tunnel Vision in Criminal Cases. *Wisconsin Law Review*.
3. Dror, I. et al. (2015). [Context Management Toolbox: A Linear Sequential Unmasking (LSU) Approach](https://onlinelibrary.wiley.com/doi/10.1111/1556-4029.12805). *Journal of Forensic Sciences*.
4. Dror, I. & Kukucka, J. (2021). [Linear Sequential Unmasking–Expanded (LSU-E)](https://pubmed.ncbi.nlm.nih.gov/34466797/). *Forensic Science International: Synergy*.
5. NATO STANAG 2511 / 영국 정보 평가의 출처 신뢰성(A–F)·정보 신뢰성(1–6) 2축 등급 체계 ("Admiralty code").
6. *R v Turnbull* [1977] QB 224 목격 신원 확인 지침과 ADVOKATE 점검표 — [Kent Police 진술 정책](https://www.kent.police.uk/foi-ai/kent-police/Policy/crime-and-intelligence/police-response-to-victims-and-witnesses-referring-to-extended-victim-services-in-kent-n15b/), [Police Station Reps wiki](https://www.policestationreps.com/wiki/doku.php?id=identification). 머리글자의 구성은 자료마다 약간 다르다.
7. Cook, R., Evett, I. W., Jackson, G., Jones, P. J. & Lambert, J. A. (1998). A hierarchy of propositions: deciding which level to address in casework. *Science & Justice* 38(4).
8. Heuer, R. J. (1999). *Psychology of Intelligence Analysis*, 8장 Analysis of Competing Hypotheses. CIA Center for the Study of Intelligence.
9. C. S. Peirce의 가추(abduction) 정식. 개관은 [Wiring the 'Why' (2026)](https://arxiv.org/abs/2604.08016).
10. 숨긴 정보 검사(Concealed Information Test) 계열 연구의 "범인만 아는 정보" 논리.
11. 로카르 교환 원칙(Edmond Locard): 접촉한 두 물체는 서로 흔적을 주고받는다.
12. Chisum, W. J. & Turvey, B. *Crime Reconstruction*. Academic Press.
13. Lee, J., Kang, M.-C. & Shin, J. (2026). [Make LLMs See Like Investigators, Not Just Think More (PRISM)](https://aclanthology.org/2026.acl-long.1056/). ACL 2026.
14. Lipton, P. (2004). *Inference to the Best Explanation* (2nd ed.). Routledge.
15. Bex, F. (2011). [*Arguments, Stories and Criminal Evidence: A Formal Hybrid Theory*](https://philpapers.org/rec/BEXASA). Springer.
16. Wagenaar, W. A., van Koppen, P. J. & Crombag, H. F. M. (1993). *Anchored Narratives: The Psychology of Criminal Evidence*. 최근 개관: van Koppen 외 (2021), [Explanation-Based Approaches to Reasoning about Evidence and Proof in Criminal Trials](https://www.petervankoppen.nl/ewExternalFiles/2021%20Explanation-Based%20Approaches%20to%20Reasoning.pdf).
17. Hazelwood, R. R. & Napier, M. R. (2004). [Crime Scene Staging and Its Detection](https://journals.sagepub.com/doi/10.1177/0306624X04268298). *International Journal of Offender Therapy and Comparative Criminology*.
18. Ferguson, C. 외. [The Defects of the Situation: A Typology of Staged Crime Scenes](https://pure.bond.edu.au/ws/portalfiles/portal/18275117/The_Defects_of_the_Situation.pdf); [Staged Homicides: Common Features of Faked Burglaries, Suicides, Accidents](https://www.researchgate.net/publication/271631179_Staged_Homicides_An_Examination_of_Common_Features_of_Faked_Burglaries_Suicides_Accidents_and_Car_Accidents).
19. Arthur Conan Doyle, "Silver Blaze" (1892).
20. US Government (2009). *A Tradecraft Primer: Structured Analytic Techniques for Improving Intelligence Analysis* — Key Assumptions Check.
21. Klein, G. (2007). Performing a Project Premortem. *Harvard Business Review*.
22. Pennington, N. & Hastie, R. 이야기 모델(story model) — [Hastie (편), *Inside the Juror*](https://www.marcellodibello.com/legal-probabilism/readings/Hastie-story-model.pdf).
23. [PLAYER\*](https://arxiv.org/abs/2404.17662) (2024): 정보 이득이 큰 질문을 고르는 머더 미스터리 에이전트.
24. [Don't Let Me Ask for It](https://arxiv.org/abs/2608.03388) (2026): LLM의 능동적 정보 수집 결함.
25. Bogaard, G., Meijer, E., Vrij, A. & Merckelbach, H. (2016). [Scientific Content Analysis (SCAN) Cannot Distinguish Between Truthful and Fabricated Accounts of a Negative Event](https://www.frontiersin.org/articles/10.3389/fpsyg.2016.00243/full). *Frontiers in Psychology*.
26. Amado, B. G., Arce, R., Fariña, F. & Vilariño, M. (2016). [CBCA reality criteria in adults: A meta-analytic review](https://www.sciencedirect.com/science/article/pii/S1697260016000041). *International Journal of Clinical and Health Psychology*.
27. DePaulo, B. M. 외 (2003). Cues to deception. *Psychological Bulletin*.
