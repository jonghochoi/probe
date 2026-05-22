# vendor/lerobot/

Read-only reference snapshot of selected `lerobot` policy code. PROBE itself
is a Korean paper-analysis + scouting framework and does not run this code —
it is vendored as the **v0 foundry**, so the `/foundry` command can map a
Design (Layer 1, vendor-agnostic) onto **concrete file/line locations** of a
known baseline, and emit an implementation guide
(`analysis/<id>_impl/lerobot/impl.md`) plus a unified-diff patch
(`impl.patch` next to it) against this snapshot.

## Provenance

| Field | Value |
|---|---|
| Source repository | `jonghochoi/lerobot` (fork of `huggingface/lerobot`) |
| Pinned commit | `999e77ad7bc30774cccca58bd29f732a90600931` |
| Vendor date | 2026-05-20 |
| License | Apache-2.0 (see `LICENSE`; original headers preserved in each file) |
| Scope | 6 baseline policies + `rtc/` + shared base + `configs/` + `processor/` + `datasets/` + `transforms/` + `utils/` |

## What is vendored

```
vendor/lerobot/
├── LICENSE                                      Apache-2.0 (verbatim from lerobot)
├── policies/
│   ├── __init__.py
│   ├── pretrained.py                            PreTrainedPolicy base class
│   ├── factory.py                               policy registry / loader
│   ├── utils.py                                 shared helpers
│   ├── pi_gemma.py                              Gemma modules shared by pi0/pi05/pi0_fast
│   ├── pi0/                                     openpi π0 (configuration/modeling/processor)
│   ├── pi05/                                    openpi π0.5
│   ├── pi0_fast/                                openpi π0-FAST
│   ├── smolvla/                                 SmolVLA (incl. smolvlm_with_expert.py)
│   ├── act/                                     Action Chunking Transformer (ALOHA)
│   ├── diffusion/                               Diffusion Policy
│   └── rtc/                                     Real-Time Chunking — inpainting/prefix-attention real-time inference for action-chunking policies
├── configs/                                     PreTrainedConfig, FeatureType, PolicyFeature, …
├── processor/                                   normalization + tokenization pipeline
├── datasets/                                    LeRobotDataset — the de-facto standard robot-learning dataset format (load/read/write/stream/aggregate/tools)
├── transforms/                                  image transforms (augmentation) referenced by datasets
└── utils/                                       shared constants + helpers (constants, import_utils, io_utils, feature_utils, hub, action_interpolator, …)
```

Not vendored: `lerobot.optim`, `lerobot.model`, `lerobot.envs`, `lerobot.types`,
`lerobot.rl`, robot drivers, training scripts, tests. The vendored `.py` files
still `import` from those modules — that is intentional: the snapshot is for
**reading and diff'ing**, not for running. If you want to actually execute any
of this code, install `lerobot` from the pinned commit instead of relying on
this directory.

## Why it is here

`/foundry` reads a Layer 1 Design (`analysis/<id>_design.md`), identifies
whether the Design can ground in one of the six policies above (the
`foundry=lerobot` case), then produces a
Korean implementation guide whose code references point inside this
directory. The patch (`impl.patch`) is generated against the current state
of this snapshot, so the snapshot itself must stay byte-stable until the
patch is regenerated.

## Refreshing the snapshot

Bumping the pinned commit invalidates every existing `impl.patch` under
`*/lerobot/impl.patch`. The intended cadence is **rare**: only when an
upstream `lerobot` change is needed to support a new Design's baseline.

Procedure:

1. Update `jonghochoi/lerobot` to the desired commit and note its SHA.
2. From the lerobot checkout, overwrite the seven policy directories
   (`pi0`, `pi05`, `pi0_fast`, `smolvla`, `act`, `diffusion`, `rtc`) plus the
   policy-level shared files (`pretrained.py`, `factory.py`, `utils.py`,
   `pi_gemma.py`, `__init__.py`) and the `configs/`, `processor/`, `datasets/`,
   `transforms/`, and `utils/` trees under `vendor/lerobot/`. Do not modify the
   files by hand — they must remain byte-identical to upstream so attribution
   stays clean. One exception, applied consistently with the existing snapshot:
   each policy's `README.md` is a symlink into `docs/source/` upstream; resolve
   it to the real file content when copying (the snapshot has no `docs/` tree).
3. Replace `LICENSE` if upstream changed it (it has not, at the pinned
   commit, but check).
4. Update **Pinned commit** and **Vendor date** in the table above.
5. Re-run `/foundry <design-path> --foundry lerobot` for every Design that
   already has an `impl.md` under `*/lerobot/`, and verify the regenerated
   `impl.patch` still applies cleanly to the new snapshot. Then re-run
   `/verify <design-path> --foundry lerobot` so `manifest.implementation.
   lerobot.apply_check` and `manifest.validation.lerobot.*` reflect the
   refreshed state. Patches that no longer apply must be rebuilt; their
   guide files keep `(잠정)` markers until they are.

## License & attribution

Apache-2.0. The full text is in `LICENSE`. Every `.py` file carries its
original `# Copyright …` header from upstream — those headers must not be
removed when refreshing the snapshot. Modifications inside this directory
are forbidden (see step 2 above): the only way it changes is a wholesale
overwrite from a newer upstream commit.
