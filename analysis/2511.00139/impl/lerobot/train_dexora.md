# pi0_enhance × Dexora 실세계 데이터 — 학습 런북

## 🧭 구성

- **lerobot**: 내 체크아웃에 `impl.patch` 적용 → `pi0_enhance` 등록 + lerobot 학습 CLI 로 실행.
- **Dexora**: 데이터 소스 (LeRobotDataset). task 한 폴더 = `DATASET_DIR`.
- **pretrained**: `lerobot/pi0_base` (PaliGemma-3B + action expert, ~3.5B), HF 캐시에서 로드.

## 🔧 데이터 차원 — Dexora 39-DoF

| 인덱스 | 관절 | 그룹 | aux supervision |
|--------|------|------|-----------------|
| `[0:6)` · `[6:12)` | left/right arm 1..6 | 양팔 | enhance: L_main + L_arm |
| `[12:24)` · `[24:36)` | left/right hand 1..12 | 양손 | enhance: L_main + L_hand |
| `[36:38)` · `[38:39)` | head 1..2 · spine | 머리·척추 | L_main only (양쪽 동일) |

스크립트 기본값: `arm_dim=12`, `max_state_dim=40`, `max_action_dim=40`.

## 📦 lerobot 설치 (uv)

```bash
cd ~/dev/lerobot
uv python pin 3.12     # 3.13/3.14 는 draccus 와 충돌
uv sync --locked --extra pi --extra dataset --extra training
```

- extra 3개 (`pi` + `dataset` + `training`) 필수.
- `--all-extras` 금지 — `groot` 의 `flash-attn` 빌드 실패, pi0 학습엔 불필요.
- editable 자동 → 패치한 `modeling_pi0_enhance.py` 그대로 import.

## 🔄 데이터 변환 v2.1 → v3.0

Dexora 는 v2.1, fork 의 lerobot 은 v3.0 → 학습 전 변환 필수.

```bash
LEROBOT_PY=~/dev/lerobot/.venv/bin/python \
  bash convert_all_dexora.sh \
       /path/to/Dexora_Real-World_Dataset \
       airbot_dexterous \
       dexora/<task>
```

- 변환은 `--root` 위치에 in-place (staging `_v30` 폴더는 자동 정리).
- 멱등 — 이미 v3.0 이면 skip.
- 학습 시 `DATASET_DIR=<원래 root>` (접미사 없음).

## 🚀 학습 실행

### 필수 env

| 변수 | 예시 |
|------|------|
| `LEROBOT_SRC` | `~/dev/lerobot` |
| `LEROBOT_PY` | `~/dev/lerobot/.venv/bin/python` |
| `DATASET_DIR` | `/data/.../dexora/<task>` |

### base vs enhance (동일 SEED·STEPS·BATCH, `POLICY_TYPE` 만 다름)

```bash
export HF_HUB_OFFLINE=1
export WANDB_MODE=offline

COMMON="LEROBOT_SRC=~/dev/lerobot LEROBOT_PY=~/dev/lerobot/.venv/bin/python \
        DATASET_DIR=/data/.../dexora/<task> \
        SEED=42 STEPS=5000 BATCH_SIZE=8 NUM_WORKERS=4 USE_AMP=true \
        TRAIN_EXPERT_ONLY=true GRADIENT_CHECKPOINTING=true \
        LOG_FREQ=50 SAVE_FREQ=2500 WANDB=true RUN_SMOKE=0"

CUDA_VISIBLE_DEVICES=0 env $COMMON POLICY_TYPE=pi0         OUTPUT_DIR=outputs/base \
  bash setup_and_train.sh 2>&1 | tee outputs/base.log

CUDA_VISIBLE_DEVICES=1 env $COMMON POLICY_TYPE=pi0_enhance OUTPUT_DIR=outputs/enhance \
  bash setup_and_train.sh 2>&1 | tee outputs/enhance.log
```

- 인덱스 혼동 방지: `export CUDA_DEVICE_ORDER=PCI_BUS_ID` 한 줄 권장.
- 스크립트는 stdout 로그 외에 `OUTPUT_DIR/checkpoints/` 도 저장.

## 🔁 pretrained fine-tuning

`PRETRAINED=lerobot/pi0_base` 기본값. 비-strict 로드:
- backbone (PaliGemma + expert) 전이됨 — 777 키.
- `state_proj` / `action_in_proj` / `action_out_proj` (32→40) shape mismatch → 재초기화.
- enhance: `feature_enhancer.*` 헤드 fresh init.

`PRETRAINED=` (빈값) → scratch 학습.

## 🧪 실험 매트릭스

### Stage 별

| Stage | 데이터 | STEPS | 목적 |
|-------|--------|-------|------|
| 0 (smoke) | 가장 작은 task | 200 | 파이프라인 검증 |
| 1 | 작은 dexterous task | 5k | loss 추이·OOM 헤드룸 |
| 2 | 중간 단일 task | 20k | 비교 + λ sweep |
| 3 | `airbot_dexterous` 카테고리 | 40–80k | mixed-task 비교 |

### λ sweep (Stage 2 에서만)

```bash
for L in 0.0 0.1 0.5 1.0 2.0; do
  env $COMMON POLICY_TYPE=pi0_enhance AUX_LOSS_WEIGHT=$L \
    OUTPUT_DIR=outputs/enhance_lam${L} bash setup_and_train.sh
done
```

`λ=0` = enhancer 아키텍처만 살아있고 보조 감독 OFF (통제군).

### 비교 지표

손 인덱스 `[12:36)` 의 `loss_per_dim` 평균을 base vs enhance:

```python
import json
d = json.load(open('outputs/<run>/wandb/latest-run/files/wandb-summary.json'))
lpd = [d[f'train/loss_per_dim/{i}'] for i in range(40)]
print('hands [12:36) mean=', sum(lpd[12:36]) / 24)
```

> 필요: fork 의 `src/lerobot/common/wandb_utils.py` 에서 numeric list 를
> per-index key (`loss_per_dim/0`, `loss_per_dim/1`, …) 로 풀도록 1곳 패치.
> 기본 래퍼는 list 타입을 버려서 `loss_per_dim` 이 기록되지 않습니다.

## 🚚 오프라인 GPU 서버로 이전 (uv)

```bash
# 로컬 (인터넷 됨) — 패키징
tar czf /tmp/lerobot-src.tar.gz -C ~/dev --exclude=lerobot/.venv lerobot
tar -cf - -C ~/.cache uv          | ssh server 'tar -xf - -C ~/.cache/uv-cjh --strip-components=1'
tar -cf - -C ~/.cache huggingface | ssh server 'tar -xf - -C ~/.cache'
rsync -avz --exclude='*_v30' /path/to/Dexora_v30/<task>/ server:/path/

# 서버 (오프라인) — 재구성
export UV_CACHE_DIR=~/.cache/uv-cjh
cd ~/dev/lerobot
uv python pin 3.12
uv sync --locked --offline --extra pi --extra dataset --extra training
```

build wheel (`setuptools`/`wheel`/`pip`) 이 캐시에 없을 때:

```bash
# 로컬에서 받아 옮기기
pip download -d /tmp/build-wheels --no-deps --only-binary :all: \
  --python-version 3.12 --platform linux_x86_64 setuptools wheel pip
# 서버에서
uv sync --locked --offline --find-links /tmp/build-wheels \
  --extra pi --extra dataset --extra training
```

## 🩹 패치 수동 적용

```bash
# 시험
git -C ~/dev/lerobot apply -p3 --directory=src/lerobot --check \
  < ~/dev/probe/analysis/2511.00139/impl/lerobot/impl.patch
# 실제 적용
git -C ~/dev/lerobot apply -p3 --directory=src/lerobot \
  < ~/dev/probe/analysis/2511.00139/impl/lerobot/impl.patch
# 이미 적용됐는지 확인
git -C ~/dev/lerobot apply -p3 --directory=src/lerobot --reverse --check \
  < ~/dev/probe/analysis/2511.00139/impl/lerobot/impl.patch
```

flat-layout 이면 `--directory=lerobot`. `--check` 거부 = 버전 불일치 →
`git checkout 999e77a` 또는 두 seam 손으로 이식 (impl.md §⚙️).

## ✅ 성공 기준

- import OK + `torch.cuda.is_available()` True.
- pretrained 로드 시 missing/size-mismatch 가 projection 3개 + (enhance) enhancer 헤드만.
- 학습 loss 우하향 + 체크포인트 저장.
- 손 인덱스 `[12:36)` 평균 loss 가 enhance < base.
