# VLA → Action 브리징 — DynaFLIP × VLA-Adapter × π0.5

> VL 표현을 action 으로 잇는 "브리징"은 세 직교 축의 선택이다 — **무엇을**(raw feature
> vs 학습형 query) × **어디서**(어느 레이어) × **얼마나**(주입 게이트). 이 문서는 세 논문을
> 그 축 위에 세워, DynaFLIP 의 action-aware feature 를 π0.5 액션 전문가에 엮는 두 주입
> 변종(copy-branch / bridge-attention)을 비교한다.

---

## 1. 세 점의 연결

| 논문 | 무엇을 | 어디서 | 얼마나 (게이트) | 액션 헤드 |
|---|---|---|---|---|
| **π0 / π0.5** ([arXiv:2410.24164](https://arxiv.org/abs/2410.24164)) | raw VLM feature | 전 레이어 | 게이트 없음(직접 attention) | flow-matching |
| **VLA-Adapter** ([arXiv:2509.09372](https://arxiv.org/abs/2509.09372)) | raw + 학습형 ActionQuery | 전 레이어 | raw 만 `tanh(g)`, g init 0 | L1 회귀 (Bridge Attention) |
| **DynaFLIP** ([arXiv:2605.30350](https://arxiv.org/abs/2605.30350)) | — (feature *공급자*) | — | — | — (frozen 시각 인코더) |

핵심은 DynaFLIP 이 헤드가 아니라 **조건 공급자**라는 점이다. 두 가지가 맞물린다:

1. **DINOv2 혈통.** VLA-Adapter 의 비전 인코더는 DINOv2 + SigLIP 이다([arXiv:2509.09372] design §데이터계약). DynaFLIP 은 *동역학 인식 목적으로 사전학습한 DINOv2* 이므로, VLA-Adapter 가 말하는 **"raw feature 조건"의 자리에 들어갈 — 이미 action-aware 한 — feature** 다. 즉 Bridge Attention 의 CA1(raw) 입력을 일반 DINOv2 대신 DynaFLIP 으로 교체하면, 조건 자체가 "행동이 장면을 어떻게 바꾸는가"를 담는다.

2. **같은 zero-init 주입 원리.** VLA-Adapter 의 `tanh(g)`(g=0 에서 출발) 와 DynaFLIP→π0.5 PVI([arXiv:2603.12772]) 의 zero-init 잔차 `Z_i` 는 **동일한 원리** — <cite>학습 초기 영향이 0에서 출발해 분포 안정성을 보장</cite>([arXiv:2509.09372] 가정 2), 즉 "베이스를 보존한 채 주입량을 학습". 형태만 다르다(잔차 vs 게이트된 cross-attn).

레포의 VLA-Adapter 분석이 이 결합을 이미 예고했다 — <cite>`pi0` 의 action expert 를 Bridge Attention(전 레이어 cross-attn + 학습형 ratio g)로 치환하는 변형 매핑도 가능 후보</cite> ([`analysis/2509.09372/design.md`](../2509.09372/design.md) §🔌), 그리고 <cite>frozen 백본은 last-layer 가 아니라 중간/전 레이어 특징을 cross-attn 으로 주입해야 동작</cite> ([`analysis/2509.09372/analysis.md`](../2509.09372/analysis.md) §의사결정).

---

## 2. 주입 변종 — copy-branch vs bridge-attention

둘 다 DynaFLIP 패치 토큰을 π0.5 **액션 전문가(diffusion transformer) hidden** 에 주입하고, 둘 다 zero-init→identity 에서 출발한다. 차이는 주입의 *형태*다. 구현은 [`analysis/2605.30350/impl/lerobot/impl.md`](../2605.30350/impl/lerobot/impl.md) (`dynaflip_inject_mode`).

| 축 | **copy_branch** (PVI [arXiv:2603.12772]) | **bridge_attention** (VLA-Adapter식) |
|---|---|---|
| 메커니즘 | 액션 전문가의 학습형 *복제본*이 `[aux ; action]` 위를 돌고, layer 별 hidden 을 zero-init `Z_i` 로 main 에 잔차 가산 | action 토큰이 DynaFLIP 패치 토큰에 **cross-attend**, 출력에 `tanh(g)` 게이트 |
| 학습 파라미터 | 투영 + **전문가 복제본(≈전문가 1개분)** + `Z_i` | 투영 + per-layer cross-attn + 게이트 `g` (가벼움) |
| zero-init 주체 | 투영 + `Z_i` (잔차=0) | 게이트 `g`(=0 → `tanh`=0 → 잔차=0). cross-attn 가중치는 일반 init |
| 조건 형태 | aux 가 복제 전문가의 prefix self-attention 컨텍스트 | aux 가 cross-attn 의 key/value (VLA-Adapter CA1) |
| 충실 근거 | DynaFLIP appendix(copy of action expert + 계층별 주입기) | VLA-Adapter Eq.(1) CA1·`tanh(g)` |
| 비용/검증 | 무겁고 복제본 동기화 필요 | 가볍고 게이트 항이 단위 검증 쉬움 |

**ActionQuery(CA2)** — VLA-Adapter 는 raw 외에 학습형 ActionQuery + proprio 를 두 번째 cross-attn 으로 결합하고 <cite>두 타입 동시 + 전 레이어</cite>가 최적이라 보고한다([arXiv:2509.09372] §4.5). 현재 bridge 모드는 raw(CA1)만 구현하고 CA2 는 config 자리(`dynaflip_use_action_query`)만 둔 확장 옵션이다.

---

## 3. 권고

- **bridge_attention 을 DynaFLIP 의 자연스러운 액션 맵핑 경로로.** "action-aware feature 를 액션에 엮는다"는 목표에 가장 직접적이다 — DynaFLIP 을 Bridge Attention 의 gated raw-feature 조건으로 쓰면, 동역학 인식 표현이 액션 전문가에 per-layer 로 흘러든다. copy-branch 는 충실하지만 무겁고, bridge 는 같은 zero-init 보존성을 더 싸게 얻는다.
- **기본값은 copy_branch 유지(보존), bridge 는 opt-in.** 둘 다 `inject_dynaflip=False` 면 베이스와 바이트 동일.
- **regime 사다리.** ① fine-tune 주입(VLM·main 전문가 frozen, 주입 모듈만 학습 — VLA-Adapter D19a+D20 패턴) 으로 "DynaFLIP feature 가 우리 과제에 이득인가"를 싸게 검증 → ② 이득이면 사전학습 단계로 끌어올려 액션 전문가까지 학습(이 경우 게이트·복제본의 보존 장치는 약화/해제). 자세한 보존 평면은 [`vlm-prior-preservation.md`](vlm-prior-preservation.md) path A④, PEFT 위치는 [`peft-robotics.md`](peft-robotics.md).
- **확장 옵션** — ActionQuery(CA2), 게이트 공유 vs per-layer, cross-attn projection 공유(VLA-Adapter 경량화)는 모두 미결로 두고 절제 축으로 남긴다.

---

## 검증 경계

bridge / copy-branch 의 *수치* 정합(전체 액션 전문가 forward, flow-matching 학습)은 PaliGemma/gemma 가중치가 필요해 가중치-없는 CPU smoke 범위 밖이다([`impl.md`](../2605.30350/impl/lerobot/impl.md) §🚧, foundry §G). smoke 는 구조·등록·**zero-init→identity**(게이트=0 시 잔차 정확히 0)만 보장한다. 다운스트림 weighted 런타임에서 `inject_dynaflip` on/off·`dynaflip_inject_mode` 동치(주입 초기 시점)를 회귀로 확인할 것.
