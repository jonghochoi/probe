# Design — AVP: Action with Visual Primitives

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | AVP: Action with Visual Primitives |
| 링크 | [arXiv:2605.22183](https://arxiv.org/abs/2605.22183) |
| 분석 문서 | [`analysis/2605.22183/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-08-02 |

---

## 🧮 데이터 계약

시간 축은 의미 단위(`chunk_size` = 액션 지평 `h`)로 기록합니다. 배치 `B`.

- **입력 — 관측** `o_t`: multi-view RGB, shape `(B, N_cam, 3, H, W)`, dtype `float32`, VLM 백본의 이미지 정규화 규약을 따름 (원문 `640×480`, `N_cam` = 손목 2 + 상단 1 = 3; 해상도/정규화 통계는 원문에 명시 없음 — 백본 규약 가정).
- **입력 — 언어** `l`: 토큰 시퀀스 `(B, L_text)`, 정수 토큰 id.
- **입력 — proprioception/상태** `s_t`: shape `(B, D_state)`, dtype `float32`, dataset 통계로 정규화 (dual-arm 14-dim; 정규화 통계 출처는 원문 미명시 — 데이터셋 평균/표준편차 가정).
- **입력(학습 전용) — 시각 프리미티브 라벨** `y_t^vp`: 이산화 격자 인덱스, shape `(B, N_prim)`, dtype `int64` (격자 해상도 `G` 원문 미명시).
- **중간 — 시각 프리미티브** `p_t`: 이산 토큰 시퀀스 `(B, N_prim)`; 투영 후 `z_t^vp`: 시각 토큰 `(B, N_vp_tok, D_tok)`.
- **중간 — 증강 멀티모달 표현** `z_t^aug`: `(B, N_tok, D_tok)`, `z_t^vp` 와 원 멀티모달 토큰의 융합.
- **출력 — 액션** $`a_{t:t+h}`$ : shape `(B, h, D_action)`, dtype `float32`, `D_action` = 14 (dual-arm 병렬 그리퍼); 플로우 매칭으로 생성. 정규화는 π0.5 규약 가정.

---

## 🧰 모듈 인터페이스

```python
def vlm_encode(o_t, l) -> "context_tokens":
    """멀티모달 관측·명령을 VLM 컨텍스트 토큰으로 인코딩 (사전학습 백본)."""

def primitive_decoder(context_tokens) -> "p_t":
    """VLM 컨텍스트에서 이산화 시각 프리미티브를 자기회귀 예측 (식 2, D_psi)."""

def project_primitive(p_t, o_t) -> "z_t_vp":
    """예측 프리미티브를 시각 토큰 공간으로 투영 (식 3, Proj); 언어→시각 공간 이동."""

def fuse_tokens(z_t_vp, multimodal_tokens) -> "z_t_aug":
    """시각-프리미티브 토큰과 원 멀티모달 토큰을 융합해 증강 표현 생성."""

def action_expert(z_t_aug, s_t) -> "a_{t:t+h}":
    """증강 표현 + 상태에서 액션 지평을 플로우 매칭으로 생성 (식 4, pi_theta)."""

def build_vp_label(traj) -> "y_t_vp":
    """EE 기구학에서 시각 프리미티브 라벨 자동 구성.
       (1) |Δg_t|>δ 로 키프레임 추출 (식 6)
       (2) 각 키프레임 3D EE 위치 P_t 취득 (식 7)
       (3) K·T_R^C 투시 투영 → (u_t,v_t) (식 8) → 격자 이산화."""
```

- `primitive_decoder` — 입력: VLM 컨텍스트 토큰. 출력: 이산 프리미티브 `p_t`. 외부 호출 계약: 손실 `L_vp = L_CE(p_t, y_t^vp)` 와 결합; 학습 1단계에서 단독 최적화.
- `action_expert` — 입력: `z_t_aug`, `s_t`. 출력: 액션 지평. 계약: 표준 액션 손실 `L_act`(플로우 매칭); `z_t_aug` 를 조건으로만 사용(대상 위치 추정 책임 없음).
- `build_vp_label` — 학습 파이프라인 전처리. 외부 지각 모델 호출 없음(EE proprioception + 카메라 캘리브레이션만 사용).

---

## ⛓️ 불변식·가정

- (가정 1) — VLM↔액션 전문가 책임 분리 불변식: 액션 전문가는 대상 "위치" 를 `z_t_aug` 로부터 조건으로 받을 뿐 스스로 추정하지 않는다. 이 분리가 깨지면(프리미티브 무시) AVP 는 baseline VLA 로 퇴화한다.
- (가정 2) — 지도 신뢰 불변식: 그리퍼 상태 전이 키프레임이 실제 물리적 상호작용 지점(파지/해제)과 일치한다 ( $`|\Delta g_t|>\delta`$ ⇒ 상호작용).
- (가정 3) — 기하 정합 불변식: 투영 $`z_c[u,v,1]^T = K T_R^C [P_t,1]^T`$ 가 성립하려면 $`K`$ · $`T_R^C`$ 가 데이터 수집 시점과 추론 시점에서 유효(캘리브레이션 드리프트 무시 가능)해야 한다.
- (가정 4) — 이산화 상한: 프리미티브 격자 해상도 `G` 가 태스크 요구 공간 정밀도보다 세밀하다(격자 셀 크기 < 성공 허용 오차).
- (가정 5) — VLM 공간 접지 능력: 사전학습 VLM 이 명령·관측에서 다음 단계 공간 타깃을 방출할 만큼의 공간 추론을 이미 보유한다.

---

## 📊 하이퍼파라미터·손실

- 프리미티브 손실: `L_vp = L_CE(p_t, y_t^vp)` (식 5, cross-entropy).
- 전체 손실:

$$\mathcal{L}=\mathcal{L}_{act}+\lambda\mathcal{L}_{vp}$$

- 키프레임 판정: $`T_{key} = \{ t \in [1,T] : |\Delta g_t| > \delta \}`$ (식 6).
- 투영:

```math
z_{c}\begin{bmatrix}u_{t}\\ v_{t}\\ 1\end{bmatrix}=KT_{R}^{C}\begin{bmatrix}P_{t}\\ 1\end{bmatrix}
```

| 이름 | 값 | 출처 |
|------|----|----|
| $`\lambda`$ (프리미티브 손실 가중치) | (원문 미명시) | §3.2 |
| $`\delta`$ (그리퍼 전이 임계) | (원문 미명시) | §Appendix B, Eq. (6) |
| 격자 해상도 `G` | (원문 미명시) | §Appendix B |
| batch size | `64` | §4.1, Table 8 |
| 학습 스케줄(장기) | `10k primitive + 30k joint` | §Appendix C, Table 8 |
| 학습 스케줄(도미노/일반물체/ablation) | `2.5k primitive + 7.5k joint` | §Appendix C, Table 8 |
| 학습 스케줄(공간-조합 일반화) | `12.5k primitive + 37.5k joint` (총 50k) | §Appendix C, Table 8 |
| 마스크 불투명도 $`\alpha`$ | `0` / `0.7` / `0.9` (ablation) | §A.3, Table 7 |
| 액션 손실 `L_act` | 플로우 매칭 (π0.5 규약) | §4.1 |
| action dim `D_action` | `14` (dual-arm) | §4.1 |

---

## 🎯 평가 메트릭

- **지표** — `Instruction Following` / `Pick Success` / `Place Success` 성공률(%) · 도미노는 `Instruction Following` 대신 `Orientation Success` · **임계값** — 도미노 성공: 위치 오차 ≤ 도미노 두께 1개 AND 각도 편차 `< 10°` · **비교 baseline** — π0.5 (동일 임베디먼트·데이터·프로토콜로 재현).
- **보조 지표** — `Latency`(s/step) · 공간-조합 일반화(unseen direct 전이 성공률) · 교차 도메인 일반화(unseen 물체 성공 개수/8).
- 주의 — 헤드라인 "overall" 이득이 초록/서론 37.04% vs 결론 27.61% 로 불일치(analysis §📊/⚖️ 참조). 재현 시 태스크별 평균으로 분리 보고 권장.

---

## ✨ 변경 의도 (intent)

기존 VLA 는 VLM 의 raw 특징을 액션 전문가에 그대로 흘려 "무엇을·어디서·어떻게" 를 한 학습 목표에 뒤섞습니다. AVP 는 이 경계를 **공간 접지된 시각 프리미티브 토큰**이라는 명시적 통신 채널로 치환하여, VLM 은 다음 단계 타깃을 시각 공간에 표시하고(무엇을·어디서) 액션 전문가는 표시된 곳을 실행(어떻게)하는 데만 집중하게 합니다. 언어 서브태스크(π0.5)보다 공간 구분이 정밀하고, 미래 프레임(π0.7)보다 희소하며, 캐스케이드 비주얼 프롬프트(Point-VLA)와 달리 외부 모델 없이 end-to-end 내부화됩니다. 결정적 차별점은 시각 프리미티브 라벨을 **엔드이펙터 기구학**(그리퍼 전이 키프레임 → 3D EE → 이미지 투영 → 이산화)에서 자동 유도해 수작업 주석·외부 검출기를 제거한 것입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 베이스는 `pi05` family 가 가장 근접합니다(논문이 π0.5 위에 직접 구축·baseline). 매핑 축: (1) VLM 뒤에 시각-프리미티브 자기회귀 디코더 헤드 + `L_vp` cross-entropy 보조 손실 추가, (2) 액션 전문가 조건 입력을 raw 멀티모달 토큰 → `z_t_aug`(프리미티브 융합) 로 교체, (3) 데이터 전처리에 EE-투영 프리미티브 라벨 빌더 추가, (4) 2단계 학습 스케줄(디코더 선행 → 합동). 플로우 매칭 액션 전문가는 기존 `pi05` 헤드 재사용.

---

## 🚧 미해결 / 잠정

- $`\lambda`$ (프리미티브 손실 가중치), $`\delta`$ (그리퍼 전이 임계), 프리미티브 이산화 격자 해상도 `G` 모두 원문 미명시 — 구현 시 스윕/가정 필요.
- `Proj(·)`(식 3)와 `fuse(·)`(`z_t^aug` 생성)의 구체 연산(cross-attention vs concat vs 렌더링 오버레이)이 본문에 명시되지 않음 — 융합 방식은 잠정.
- 시각 프리미티브 디코더의 구조(레이어 수·어휘 크기·프리미티브 토큰화 방식)와 `N_prim`/`N_vp_tok` 미명시.
- `L_act` 플로우 매칭 손실의 정확 형태는 π0.5 프레임워크를 따른다고만 명시(본문에 별도 수식 없음) — 가정으로 메움.
- 이미지 정규화 통계·상태 정규화 통계 출처 미명시 — 데이터셋/백본 규약으로 가정.
