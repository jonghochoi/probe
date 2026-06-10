# Design — vla-eval: A Unified Evaluation Harness for Vision-Language-Action Models

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | vla-eval: A Unified Evaluation Harness for Vision-Language-Action Models |
| 링크 | [arXiv:2603.13966](https://arxiv.org/abs/2603.13966) |
| 분석 문서 | [`analysis/2603.13966/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-04 |

> 주의 — 본 논문은 **학습 알고리즘이 아니라 평가 인프라**입니다. 따라서 손실·옵티마이저·텐서 학습 계약이 존재하지 않으며, Layer 1 Design 은 "평가 하니스의 통신·인터페이스·병렬화 계약"으로 해석해 채웁니다. 학습 알고리즘 슬롯은 정직하게 "해당 없음"으로 둡니다.

---

## 🧮 데이터 계약

평가 하니스의 데이터 계약은 client(모델 서버) ↔ server(벤치마크 컨테이너) 사이의 메시지 페이로드입니다. 학습 텐서 계약이 아니라 RPC 계약입니다.

- **메시지 봉투** — 각 메시지: `type` ∈ {`observation`, `action`, `episode_start`, `episode_end`}, 벤치마크별 `payload`, `sequence_number`, `timestamp`. 직렬화 = msgpack(binary), 전송 = WebSocket.
- **입력(observation payload)** — `obs["images"]`: 카메라명 → 이미지 배열(dtype·해상도는 벤치마크별, 원문 미명시; OpenVLA 예시는 단일 이미지를 `Image.fromarray`로 변환), `obs["task_description"]`: 자연어 instruction(str), proprioceptive state(채널 구성은 벤치마크별 — 원문에 통일 schema 명시 없음). action space 차원: 6D~14D(Table I).
- **출력(action payload)** — `{"actions": act}`. 7D가 다수(LIBERO/CALVIN/SimplerEnv), RoboTwin 2.0 14D, Kinetix 6D, 일부 8D. action chunking 은 베이스 클래스가 자동 처리. absolute vs. delta 모드는 **payload만으로 구분 불가**(둘 다 같은 차원의 유효 벡터) → config로 외부 지정 필수.
- **시간 축** — 의미 단위로 episode 경계(`episode_start`/`episode_end`)와 per-step observation/action 교환. 절대 timestep 좌표 없음. action chunking 의 chunk 길이는 원문 미명시.
- **결과 산출물** — 매 실행이 구조화 JSON: 하니스 버전 + 벤치마크 구성 + per-episode 메트릭. 단일 config 파일에서 정확 재현.

---

## 🧰 모듈 인터페이스

두 개의 단일-접점 인터페이스가 전체 설계의 핵심입니다.

```python
class PredictModelServer:
    """모델 통합의 단일 접점. 서브클래스는 predict() 만 구현(보통 ~50줄).
       action chunking·배치 추론(max_batch_size)은 베이스가 제공."""
    def predict(self, obs: dict, ctx: dict) -> dict:
        """obs(observation payload) → {"actions": <array>}. blocking."""
```

```python
class BenchmarkInterface:
    """벤치마크 통합의 단일 접점. 핀 고정 의존성을 가진 전용 Docker
       이미지 안에서 네 메서드만 구현하면 교차평가 행렬에 자동 편입."""
    def reset(self): ...
    def step(self, action): ...
    def make_obs(self): ...          # observation payload 구성
    def get_step_result(self): ...   # per-step 결과/메트릭 산출
```

- **모델 서버** — 역할: 추론. 입력: observation payload + ctx. 출력: action payload. 외부 계약: PEP 723 inline 의존성 선언 → `uv run`으로 격리 환경 자동 생성. 충돌 의존성(`transformers==4.40.1` vs `>=4.44`) 공존.
- **벤치마크** — 역할: 환경 실행/스코어링. 4-메서드 계약. 외부 계약: Docker 격리(ghcr.io 버전 태그) + 에셋 번들.
- **드라이버** — `vla-eval serve`(모델 서버 기동) + `vla-eval run`(평가 실행). 구동 입력: YAML config 2개(benchmark + model server).
- **병렬화 모듈** — episode sharding(환경: $`K`$ 개 컨테이너) + batch inference(추론: 배치 $`B`$). demand/supply 튜너가 운영점 $`K^{*}`$ 선택.

---

## ⛓️ 불변식·가정

- **(가정 1) 디커플링 정확성** — 모델 서버를 통과한 평가 점수는 레퍼런스 구현 점수와 동등해야 한다(검증 결과 대부분 Δ ≲ 1pp). 통신·격리 계층은 모델 출력을 변형하지 않는다 — 이것이 프레임워크 충실도의 핵심 불변식이다.
- **(가정 2) 모델-비종속 가속** — 모델 공급 천장 $`\mu(B)`$ 가 모든 샤드 수에서 환경 수요 $`\lambda(K)`$ 를 초과($`\mu(B) > \lambda(K)`$ 운영 영역)하므로, 가속이 환경 병렬화에만 좌우되고 어떤 모델에도 전이된다.
- **(가정 3) 운영점 안정 영역** — $`K`$ 증가가 throughput을 단조 증가시키지 않는다. $`K \approx 80`$ 초과 시 환경 오버헤드로 throughput 하락 → $`K^{*}`$ 는 공급 용량의 일부(예 78%)만 쓰는 지점으로 잡아 burst 흡수 여유 확보.
- **(가정 4) action 모드 비식별성** — absolute action과 delta action은 동일 차원의 유효 벡터라 **데이터만으로 구분 불가**. 잘못 가정하면 position 누적으로 robot이 발산해 0%까지 떨어지므로, 모드는 config 외부 지정이 불변 전제.
- **(가정 5) proprio/rotation 규약 일치** — proprioceptive state source와 quaternion→axis-angle 규약(`angle ∈ [0,2π]` vs `[0,π]`)이 시뮬레이터 컨벤션과 일치해야 한다. 불일치 시 −55pp / 95→56% 등 붕괴.

---

## 📊 하이퍼파라미터·손실

- 손실 식: **해당 없음** (평가 인프라 — 학습 손실/옵티마이저 없음).
- 병렬화 파라미터:

  | 이름 | 값 | 출처 |
  |------|----|----|
  | `K` (episode shards) | LIBERO 50 / CALVIN 16 / SimplerEnv 16 | §II-C |
  | `K*` (operating point) | 50 (공급 용량 78% @ B=16) | §II-C, Fig.1 |
  | `K` 상한 | 약 80 초과 시 throughput 하락 | §II-C, Fig.1 |
  | `B` (batch size) | 16 (LIBERO 측정) | §II-C, Fig.2 |
  | `max_batch_size` | (모델 서버별 설정값, 구체값 원문 미명시) | §II-A |
  | $`\lambda`$ (env throughput) | K:1→50 시 11.2→364.6 obs/s (32.6×) | §II-C |
  | $`\mu`$ (model throughput) | B:1→16 시 165.2→468.2 obs/s (2.8×) | §II-C |
  | action chunk 길이 | (원문 미명시) | — |
  | center crop scale (OpenVLA) | 0.9 (eval-time, 누락 시 ~3pp 손실) | §III-B |

- 가속 결과 식(개념): wall-clock 47× = 환경 32.6× × 배치 기여의 결합(2,000 ep, 14h → 18min).

---

## 🎯 평가 메트릭

- **지표** — `task success rate` (%) · **임계값** — published score 대비 Δ가 작을수록 충실(검증 Δ: OpenVLA −0.3, $`\pi_{0.5}`$ +0.8, OpenVLA-OFT −0.4, X-VLA −0.7 등 대부분 1pp 안팎) · **비교 baseline** — 각 코드베이스의 reported published score.
- **지표(보조)** — `CALVIN sequence length` (chained, 최대 5; X-VLA 4.30, DB-CogACT 4.02) · `throughput` (obs/s) · `wall-clock speedup` (×).
- **벤치마크 단위** — LIBERO 4 suites × 10 tasks × 50 ep (2,000); CALVIN ABC→D 1,000 chained seq; SimplerEnv 4 WidowX tasks × 24 ep.
- **미지원(저자 명시 한계)** — subtask progress, task efficiency, safety. contact-precision(slip/pose) 류 미세 메트릭 없음 → 우리 falsifier(D25)에는 자력 보완 필요.
- **리더보드 메트릭** — 17 benchmarks · 657 results · 509+ configs · 1,704 인용 논문에서 추출. 정규 프로토콜(canonical protocol) 정의로 task subset/metric/split 통일.

---

## ✨ 변경 의도 (intent)

기존 평가는 모델 `N` × 벤치마크 `M`의 각 조합마다 의존성·전처리·프로토콜을 따로 맞춰 `O(N×M)` 통합 부담을 지웠습니다. 여기서는 `lm-evaluation-harness`의 디커플링을 VLA로 옮겨, 모델 추론(WebSocket+msgpack 서버)과 벤치마크 실행(Docker 격리 + 4-메서드 인터페이스)을 별도 계층으로 나눕니다. 모델은 한 번(`predict()`), 벤치마크는 한 번(4-메서드)만 통합하면 전체 교차평가 행렬이 자동으로 작동하고, 통합 비용은 `O(N+M)`로 압축. episode sharding + batch inference로 환경 병목을 깨면 모델-비종속 47× 가속이 따라오며, 단일 미문서화 파라미터가 성공률을 최대 55pp 흔드는 재현 함정을 체계적으로 카탈로그화합니다. prior art(개별 벤치마크 러너, AutoEval식 자동 채점) 대비 차별점은 "메트릭을 풍부하게"가 아니라 "교차평가 실행 자체를 싸고 재현 가능하게" 만드는 인프라를 갖추는 데 있습니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 직접 매핑 대상이 아님(학습 정책이 아니라 평가 하니스). `lerobot` 의 정책 family(`pi0`/`pi05`/`pi0_fast`/`smolvla`/`act`/`diffusion`)는 *평가 대상*으로 vla-eval의 `PredictModelServer.predict()` 뒤에 래핑될 후보일 뿐, 본 Design 이 `lerobot` 코드에 알고리즘을 이식하는 대상은 아님. `/implement-design`은 `🚧 매핑 불가`(평가 인프라 — 정책 이식 대상 아님)로 판정할 가능성이 높음. 활용 경로는 역방향 — `lerobot` 정책을 vla-eval 모델 서버로 노출하는 어댑터.

---

## 🚧 미해결 / 잠정

- action chunk 길이, `max_batch_size` 기본값, observation 이미지 dtype/해상도의 통일 schema 는 본문에 명시되지 않아 비워둠.
- proprioceptive state 의 통일 채널 구성(어떤 모달리티가 몇 차원으로 들어가는지)은 벤치마크별로 다르며 원문에 단일 schema 없음 — "벤치마크별 정의" 로 가정.
- 47× 가속의 배치-기여 분해(환경 32.6× × 배치 X× = 47×)에서 배치 단독 기여 배수는 본문이 결합 결과만 제시 — 분해값은 가정으로 메우지 않음.
- Isaac Sim/Isaac Lab 계열 벤치마크의 1급 지원 여부는 본문 미언급(지원 14개는 robosuite/SAPIEN/PyBullet 계열) — 우리 스택 통합 비용은 미지수.
