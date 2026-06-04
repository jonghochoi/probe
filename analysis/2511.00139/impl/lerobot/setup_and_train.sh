#!/usr/bin/env bash
# pi0_enhance(2511.00139) × Dexora — local GPU training driver.
#
# Applies impl.patch to your lerobot checkout (idempotent), runs an import
# sanity check, optionally runs the CPU smoke test, then launches training.
#
# Required env: LEROBOT_SRC (your lerobot repo root), LEROBOT_PY (its venv
# python — install with `uv sync --locked --extra pi --extra dataset
# --extra training` after `uv python pin 3.12`), DATASET_DIR (one Dexora
# task folder containing meta/info.json, already v3.0).
#
# The base / lambda=0 / enhance ablation is just three flag combos, same
# COMMON env (identical SEED/STEPS/BATCH_SIZE/data so the comparison holds).
# Pin each to a GPU with GPU=0 / GPU=1 to run two at once on one node:
#   COMMON="LEROBOT_SRC=~/dev/lerobot LEROBOT_PY=~/dev/lerobot/.venv/bin/python \
#           DATASET_DIR=/data/.../dexora/<task> SEED=42 STEPS=20000 BATCH_SIZE=8 \
#           WANDB=true WANDB_MODE=offline"
#   base : env $COMMON GPU=0 POLICY_TYPE=pi0                              OUTPUT_DIR=outputs/s1_base    bash setup_and_train.sh
#   lam0 : env $COMMON GPU=1 POLICY_TYPE=pi0_enhance AUX_LOSS_WEIGHT=0.0  OUTPUT_DIR=outputs/s1_lam0    bash setup_and_train.sh
#   enh  : env $COMMON GPU=0 POLICY_TYPE=pi0_enhance AUX_LOSS_WEIGHT=1.0  OUTPUT_DIR=outputs/s1_enhance bash setup_and_train.sh
set -euo pipefail

# ── Required ──────────────────────────────────────────────────────────
LEROBOT_SRC="${LEROBOT_SRC:?set LEROBOT_SRC to your lerobot repo root}"
LEROBOT_PY="${LEROBOT_PY:?set LEROBOT_PY to its venv python}"
DATASET_DIR="${DATASET_DIR:?set DATASET_DIR to one Dexora task folder (holding meta/info.json)}"

# ── Tunable ───────────────────────────────────────────────────────────
POLICY_TYPE="${POLICY_TYPE:-pi0_enhance}"   # pi0 or pi0_enhance
PRETRAINED="${PRETRAINED:-lerobot/pi0_base}" # "" for from-scratch
FEATURE_ENHANCEMENT="${FEATURE_ENHANCEMENT:-true}"
ARM_DIM="${ARM_DIM:-12}"                # both arms = [0:ARM_DIM); hand = [ARM_DIM:action_dim) auto
AUX_LOSS_WEIGHT="${AUX_LOSS_WEIGHT:-1.0}"
MAX_STATE_DIM="${MAX_STATE_DIM:-40}"    # >= Dexora 39
MAX_ACTION_DIM="${MAX_ACTION_DIM:-40}"  # >= Dexora 39
BATCH_SIZE="${BATCH_SIZE:-8}"
NUM_WORKERS="${NUM_WORKERS:-2}"
STEPS="${STEPS:-80000}"
TRAIN_EXPERT_ONLY="${TRAIN_EXPERT_ONLY:-true}"      # VLM frozen; expert + projections (+enhancer) trained
GRADIENT_CHECKPOINTING="${GRADIENT_CHECKPOINTING:-true}"
OUTPUT_DIR="${OUTPUT_DIR:-outputs/pi0_enhance_dexora}"
DEVICE="${DEVICE:-cuda}"
GPU="${GPU:-}"                          # pin to ONE gpu index (e.g. 0 or 1); blank = all visible
SEED="${SEED:-}"                        # same value for base vs enhance
USE_AMP="${USE_AMP:-}"
LOG_FREQ="${LOG_FREQ:-}"                # blank = lerobot default (200)
SAVE_FREQ="${SAVE_FREQ:-}"              # blank = lerobot default (20000)
WANDB="${WANDB:-}"                      # also: export WANDB_MODE=offline
RUN_SMOKE="${RUN_SMOKE:-1}"
REPO_ID="${REPO_ID:-Dexora/Dexora_Real-World_Dataset}"

# ── Pin to one GPU (so two runs can share a node on index 0 and 1) ─────
# CUDA_VISIBLE_DEVICES makes the chosen card the only visible one, so it
# appears as cuda:0 inside the process and DEVICE=cuda still works.
if [ -n "$GPU" ]; then
  export CUDA_VISIBLE_DEVICES="$GPU"
  echo "==> pinned to GPU $GPU (CUDA_VISIBLE_DEVICES=$GPU)"
fi

# ── Resolve paths ─────────────────────────────────────────────────────
REPO_ROOT="$(git rev-parse --show-toplevel)"
PATCH="$REPO_ROOT/analysis/2511.00139/impl/lerobot/impl.patch"
SMOKE="$REPO_ROOT/analysis/2511.00139/impl/lerobot/test_pi0_enhance_smoke.py"

SRC="$LEROBOT_SRC"
PY="$LEROBOT_PY"
[ -d "$SRC" ] || { echo "ERROR: LEROBOT_SRC '$SRC' is not a directory"; exit 1; }
[ -x "$PY" ] || command -v "$PY" >/dev/null 2>&1 || { echo "ERROR: LEROBOT_PY '$PY' is not executable"; exit 1; }

if   [ -d "$SRC/src/lerobot/policies/pi0" ]; then PKG_DIR="src/lerobot"
elif [ -d "$SRC/lerobot/policies/pi0" ];     then PKG_DIR="lerobot"
else
  echo "ERROR: cannot find lerobot/policies/pi0 under $SRC"
  exit 1
fi
echo "==> lerobot: $SRC   pkg dir: $PKG_DIR   python: $PY"

# ── 1. Apply impl.patch (idempotent) ──────────────────────────────────
echo "==> [1/4] apply impl.patch (--directory=$PKG_DIR)"
if git -C "$SRC" apply -p3 --directory="$PKG_DIR" --reverse --check "$PATCH" >/dev/null 2>&1; then
  echo "    patch already applied — skipping"
elif git -C "$SRC" apply -p3 --directory="$PKG_DIR" --check "$PATCH" >/dev/null 2>&1; then
  git -C "$SRC" apply -p3 --directory="$PKG_DIR" "$PATCH"
  echo "    patch applied"
else
  echo "ERROR: impl.patch does not apply cleanly to $SRC."
  echo "       The two in-place seams are pinned to lerobot commit 999e77a."
  echo "       Either: git -C $SRC checkout 999e77a, or hand-port the two"
  echo "       seams (see impl.md §⚙️)."
  exit 1
fi

# ── 2. Import + CUDA sanity check ─────────────────────────────────────
echo "==> [2/4] import + CUDA check (in $PY)"
"$PY" - <<'PYEOF' || { echo "    import failed"; exit 1; }
import torch
from lerobot.policies.pi0.modeling_pi0_enhance import PI0EnhancePolicy
print("    lerobot pi0_enhance import OK")
print("    torch", torch.__version__, "cuda", torch.cuda.is_available())
PYEOF

# ── 3. (optional) CPU smoke test ──────────────────────────────────────
if [ "$RUN_SMOKE" = "1" ]; then
  echo "==> [3/4] smoke test (expect 6 passed)"
  "$PY" -m pytest "$SMOKE"
else
  echo "==> [3/4] smoke test skipped (RUN_SMOKE=0)"
fi

# ── 4. Train ──────────────────────────────────────────────────────────
[ -f "$DATASET_DIR/meta/info.json" ] || {
  echo "ERROR: $DATASET_DIR/meta/info.json not found (DATASET_DIR must be one task folder)"
  exit 1
}
echo "==> [4/4] train  (type=$POLICY_TYPE  pretrained=${PRETRAINED:-<scratch>})"

ARGS=(
  --policy.type="$POLICY_TYPE"
  --policy.max_state_dim="$MAX_STATE_DIM"
  --policy.max_action_dim="$MAX_ACTION_DIM"
  --policy.train_expert_only="$TRAIN_EXPERT_ONLY"
  --policy.gradient_checkpointing="$GRADIENT_CHECKPOINTING"
  --policy.push_to_hub=false
  --policy.device="$DEVICE"
  --dataset.repo_id="$REPO_ID"
  --dataset.root="$DATASET_DIR"
  --batch_size="$BATCH_SIZE"
  --num_workers="$NUM_WORKERS"
  --steps="$STEPS"
  --output_dir="$OUTPUT_DIR"
)
[ -n "$PRETRAINED" ] && ARGS+=( --policy.pretrained_path="$PRETRAINED" )
if [ "$POLICY_TYPE" = "pi0_enhance" ]; then
  ARGS+=(
    --policy.feature_enhancement="$FEATURE_ENHANCEMENT"
    --policy.arm_dim="$ARM_DIM"
    --policy.aux_loss_weight="$AUX_LOSS_WEIGHT"
  )
fi
[ -n "$SEED" ]      && ARGS+=( --seed="$SEED" )
[ -n "$USE_AMP" ]   && ARGS+=( --policy.use_amp="$USE_AMP" )
[ -n "$LOG_FREQ" ]  && ARGS+=( --log_freq="$LOG_FREQ" )
[ -n "$SAVE_FREQ" ] && ARGS+=( --save_freq="$SAVE_FREQ" )
[ -n "$WANDB" ]              && ARGS+=( --wandb.enable="$WANDB" )
[ -n "${WANDB_MODE:-}" ]     && ARGS+=( --wandb.mode="$WANDB_MODE" )

VENV_BIN="$(dirname "$PY")"
if [ -x "$VENV_BIN/lerobot-train" ]; then
  RUN=( "$VENV_BIN/lerobot-train" )
elif "$PY" -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('lerobot.scripts.lerobot_train') else 1)" 2>/dev/null; then
  RUN=( "$PY" -m lerobot.scripts.lerobot_train )
else
  RUN=( "$PY" -m lerobot.scripts.train )
fi
echo "    entrypoint: ${RUN[*]}"
"${RUN[@]}" "${ARGS[@]}"
