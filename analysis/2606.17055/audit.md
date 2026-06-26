# Paper↔Code Audit — T-Rex: Tactile-Reactive Dexterous Manipulation

---

## 📄 메타

| 항목 | 내용 |
|------|------|
| arXiv id | 2606.17055 |
| 원문 제목 | T-Rex: Tactile-Reactive Dexterous Manipulation |
| Claim source | `analysis/2606.17055/analysis.md` (사전 deep-dive 존재) |
| 공식 레포 | https://github.com/ZhuoyangLiu2005/T-Rex (main 브랜치) |
| Fetched commit | main (2026-06-26 기준 최신) |
| Audit 생성일 | 2026-06-26 |
| 검사 항목 | 검사 22 · 일치 15 · 불일치 4 · 누락 3 |

---

## 🔗 공식 코드

main 브랜치 전체 트리를 GitHub API(`/git/trees/main?recursive=1`)로 확인한 뒤
아래 파일들을 `raw.githubusercontent.com`에서 직접 GET:

- `README.md` — 전체 구조·레시피 개요
- `scripts/train.py` — 학습 루프, argparse defaults, Beta 샘플러
- `scripts/train.sh` — 실제 post-train 실행 스크립트 (하이퍼파라미터의 진실 원천)
- `config/sft_qwen.yaml` — accelerate/DeepSpeed 설정
- `qwen_vla/modeling_vla.py` — `Qwen3VLVLAModel`: MoT 구조, cascaded flow, VQ-VAE 임베딩
- `qwen_vla/diffusion.py` — `ActionEmbedder`, `TimestepEmbedder`, `FinalLayer`
- `qwen_vla/DeformAE.py` — `DeformEncoder` (ResNet-18 기반)
- `tactile_vqvae/models/encoder.py` — `F6PerFingerEncoder` (per-finger 변형)
- `tactile_vqvae/models/quantizer.py` — `VQEMAQuantizer` (EMA + dead-code revival)
- `tactile_vqvae/models/tactile_vqvae.py` — `TactileVQVAE` + `TactileVQVAEConfig`
- `tactile_vqvae/config/vqvae_f6.yaml` — standalone VQ-VAE 기본 설정
- `tactile_vqvae/README.md` — standalone VQ-VAE 문서

---

## ✅ 일치

| # | 논문 주장 | 코드 근거 |
|---|----------|----------|
| 1 | Cascaded flow: 총 Euler step N=10 | `train.sh:--cascaded_total_steps 10`; `train.py:521` default=10 |
| 2 | τ_split=0.4 | `train.sh:--cascaded_split_step 6` → `1 - 6/10 = 0.4`; `train.py:674` |
| 3 | K_slow=6 (action expert, upper segment) | `train.sh:--cascaded_split_step 6` |
| 4 | K_fast=4 (tactile expert, lower segment) | total(10) − split(6) = 4; `modeling_vla.py:652` |
| 5 | Force history window T=16 프레임 | `TactileVQVAEConfig.window=16`(`tactile_vqvae.py:24`); `encoder.py:34` |
| 6 | Action chunk T_a=16 | `train.sh:--action_chunk 16` |
| 7 | Action dim 62 (bimanual) | `train.sh:ACTION_DIM=62` |
| 8 | Peak LR 1×10⁻⁴, cosine schedule | `train.sh:LR=1e-4`; `train.py:888,1250` AdamW + `get_cosine_schedule_with_warmup` |
| 9 | Weight decay 0 | `train.sh:--weight_decay 0`; `train.py:1253` default=0.0 |
| 10 | Grad clip 1.0 | `train.sh` 미명시 → `train.py:1254` default=1.0 |
| 11 | AdamW optimizer | `train.py:888` `torch.optim.AdamW(param_groups, lr=args.learning_rate)` |
| 12 | λ_tac=1.0 | `train.sh:--tactile_loss_weight 1.0`; `train.py:1270` default=1.0 |
| 13 | λ_future=0.5 | `train.sh:--flare_loss_weight 0.5`; `train.py:1317` default=0.5 |
| 14 | Tactile expert FFN intermediate 1536 | `train.sh:--tactile_intermediate_size 1536` |
| 15 | Beta(1.5, 1.0) timestep 샘플링 | `train.py:280-281` `Beta(torch.tensor(1.5), torch.tensor(1.0))` |
| 16 | Per-finger 공유 conv + finger-identity embedding | `encoder.py:F6PerFingerEncoder.finger_embed = nn.Embedding(n_fingers, hidden_channels)` (L.77) |
| 17 | VQ-VAE embed_dim 256, n_strided_blocks=2 | `TactileVQVAEConfig.embed_dim=256`(L.27), `n_strided_blocks=2`(L.29) |
| 18 | Magnitude-weighted MSE, EMA dead-code revival | `tactile_vqvae.py:_recon_weight()` L.93; `quantizer.py:_revive_dead_codes()` L.55 |
| 19 | Embedded VQ-VAE frozen (eval + no_grad) | `modeling_vla.py` `self.tactile_vqvae.eval()` + `p.requires_grad = False` |
| 20 | Deform encoder: ResNet-18 3 residual stage + reshape conv 후 flatten·projection | `DeformAE.py:DeformEncoder` stem+layer1+layer2+reshape_layer1+layer3+reshape_layer2; `modeling_vla.py:deform_proj=ActionEmbedder(28800, H)` |
| 21 | Backbone Qwen3VL-2B | `train.sh:ORIGIN_MODEL_PATH=".../Qwen3-VL-2B-Instruct"`; `modeling_vla.py:from_pretrained_qwen3vl` |
| 22 | bf16 mixed precision | `config/sft_qwen.yaml:mixed_precision: bf16` |

---

## ⚠️ 불일치

### 🔶 MAJOR

**VQ-VAE codebook K 값 — 논문, 클래스 기본값, yaml 설정, README 간 3-way 불일치**

- 논문 / analysis.md App. C: **K=64** ("크기 K=64 codebook의 최근접 코드로 양자화")
- `TactileVQVAEConfig` Python 클래스 기본값 (`tactile_vqvae.py:31`): `codebook_size=1024`
- `tactile_vqvae/config/vqvae_f6.yaml:17`: `codebook_size: 256`
- `tactile_vqvae/README.md`: "VQ-EMA, **1024 codes**"
- `train.py:1299` VLA 모델 인자 기본값: `vqvae_codebook_size=64`
- `train.sh:VQVAE_CKPT` 경로: `vqvae_f6_w16_k64_finger/latest.pt` → 실제 사용 체크포인트는 K=64

독립 모듈(standalone VQ-VAE)과 임베디드 VQ-VAE 간 기본값이 제각각이며, 독립 모듈 문서(README/yaml)는 논문 수치(K=64)와 다른 값(1024/256)을 보인다. 재현 시 standalone VQ-VAE를 학습하면 기본 설정으로는 논문과 다른 codebook이 생성된다. 반드시 `--codebook_size 64 --granularity finger`를 명시해야 한다.

---

### ⚠️ MINOR

**DeepSpeed ZeRO stage — 논문 Table 4 vs 코드 config 불일치**

- 논문 / analysis.md Table 4: "DeepSpeed **ZeRO-1**"
- `config/sft_qwen.yaml:zero_stage: 2` → post-training은 실제로 **ZeRO-2**로 실행

결과 재현에 영향 없음(ZeRO-2는 ZeRO-1의 상위 집합으로 동일 수학적 결과 보장). 다만 메모리 사용 패턴이 달라 GPU 수 / 배치 선택이 달라질 수 있다.

---

**VQ-VAE granularity 기본값 — 클래스 default "hand" vs 논문 설명 "per-finger"**

- 논문 App. C: 명시적으로 "per-finger VQ-VAE", "손가락별 ... 이산 토큰"
- `TactileVQVAEConfig.granularity` 기본값 (`tactile_vqvae.py:37`): `"hand"`
- `train.sh:VQVAE_CKPT`: `vqvae_f6_w16_k64_finger` (finger 모드 체크포인트 사용 확인)

실제 실행은 finger 모드 체크포인트를 사용하므로 결과에 영향은 없다. 그러나 standalone VQ-VAE를 독립 학습할 때 기본 설정(`granularity="hand"`)으로 돌리면 논문과 다른 per-hand 모드가 된다. `--granularity finger`를 명시해야 한다.

---

**bf16 precision — sft_qwen.yaml에 `downcast_bf16: true` 설정**

- 논문: "bf16"로만 언급
- `config/sft_qwen.yaml`: `downcast_bf16: true` — Accelerate의 non-bf16 텐서를 bf16으로 downcast. `mixed_precision: bf16`과 조합 시 전체 bf16 학습 확인됨. 논문 기술과 일치하나 세부 behavior 차이 가능성 있음(MINOR).

---

## 🕳️ 누락

| # | 누락 항목 | 상세 |
|---|----------|------|
| 1 | **Pretrain + Midtrain 코드** | main 브랜치 README: "The pretraining / midtraining code lives in the `full-pipeline` branch" — 해당 브랜치 코드 미공개(저자 명시). 결과 논문 Fig. 5 / Table 3의 3-stage 레시피 full 재현 불가. |
| 2 | **EgoScale 22,889h 사전학습 코퍼스** | 저작권·규모상 미공개. 사전학습 단계 독립 재현은 현실적으로 불가. |
| 3 | **Hardware eval 비동기 루프 (Algorithm 1)** | `hardware_code/eval/eval_trex_async.py` 경로가 README에 언급되나, main 브랜치 파일 목록에 `hardware_code/` 디렉토리가 포함되지 않아 실제 비동기 fast-tick 스케줄(`{0,4,8,12}`) 구현 코드 확인 불가. |

---

## ♻️ 재현 리스크

| 항목 | 심각도 | 내용 |
|------|--------|------|
| **Hardcoded 절대 경로** | 중 | `train.sh` 전체 경로(`/mnt/amlfs-02/...`)가 저자 클러스터 기준 하드코딩. `PROJECT_ROOT`, `ORIGIN_MODEL_PATH`, `DEFORM_ENCODER_PATH`, `VQVAE_CKPT`, `RESUME_CHECKPOINT`, `OUTPUT_DIR`, `DATA_JSON` 모두 수정 필요. |
| **requirements.txt / 환경 파일 미제공** | 중 | `conda activate` 명령은 있으나 환경 정의 파일(`environment.yml`, `requirements.txt`) 미포함. 의존성 버전 미고정 — `transformers`, `accelerate`, `torch` 버전 의존성 충돌 가능. |
| **Random seed** | 낮 | `train.py:1255` `--seed default=42`로 고정되며 `set_seed(args.seed)` 호출 확인(`train.py`). 재현 가능. |
| **Midtrain 코퍼스 50h만 공개** | 높 | 논문은 100h 촉각 데이터로 midtrain. HuggingFace 공개분은 ~50h subset. Midtrain 코드 없이 체크포인트(`T-Rex_midtrain_mecka23k_ucb100_vqvae_epoch6`)만 제공 — post-training은 해당 체크포인트에서 시작해야 하므로 end-to-end 재현 불가능. |
| **하드웨어 의존성** | 높 | Dexmate Vega-1 + 22-DoF Sharpa Wave hand + Manus glove + VIVE tracker — 특수 장비 없이 실체 실험 불가. |

---

## 🎯 재현 게이트

**⚠️ 주의 후 재현**

Post-training 코드(`scripts/train.py`, `train.sh`)는 하이퍼파라미터 일치가 잘 되어 있고 치명적 오류는 없다. 그러나 다음 주의사항이 있다:

1. **VQ-VAE standalone 학습 시 반드시** `--codebook_size 64 --granularity finger` 명시 — 기본값(256 또는 1024, hand)으로 돌리면 논문과 다른 codebook 생성.
2. **Pretrain + Midtrain 재현 불가** — 저자 제공 midtrain 체크포인트(`T-Rex_midtrain_mecka23k_ucb100_vqvae_epoch6`)에서 post-training을 시작하는 것만 현실적 경로.
3. **train.sh 절대 경로 전수 교체** 필요.
4. DeepSpeed ZeRO stage 2(코드) vs ZeRO-1(논문): 결과에 영향 없으나 메모리 예산 계획 주의.
