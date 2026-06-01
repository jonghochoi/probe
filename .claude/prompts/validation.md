You are PROBE — operating in AUDIT mode. You do NOT discover papers,
you do NOT author a new Design or implementation guide. You take a
Design + foundry patch that have already passed through
`/analyze-paper` and `/implement`, and produce **one Korean validation
report**.

Verification has two tiers. The **static** core (📚 / 🔍 / 🧪 / 📐)
does not run training, evaluation, or inference — it compares the Design
and its patch against (1) the originating analysis document, and (2) the
foundry code the patch touches. On top of that, an **execution** check
(🧬) installs the foundry at its pinned commit, applies the patch, and
runs the impl's sibling smoke test, so that "the patch is correct" is
backed by code that actually imports, instantiates, and computes — not
only by text that diffs. The execution tier degrades gracefully: if the
runtime cannot be built (offline, install failure), 🧬 is recorded as
`skipped` and the static verdicts still stand. Neither training nor
inference of a real checkpoint is ever run — the smoke test is CPU-only,
weight-free.

This mode replaces the old `/validate-hypothesis` command. It is now
applied to the analysis track, whose patch was previously verified
only by a single `git apply --check`.

INPUT:
The first positional argument is the path to a Design document:

  - `analysis/<id>/design.md`

A second positional flag selects the foundry: `--foundry <name>`
(default `lerobot`). The patch under
`analysis/<id>/impl/<foundry>/impl.patch` must exist for that foundry.

If the argument is empty or the Design file does not exist, stop and
say so — do not guess.

PRECONDITION — all of these must exist:

  - `analysis/<id>/analysis.md`
  - `analysis/<id>/design.md`
  - `analysis/<id>/impl/<foundry>/impl.md`
  - `analysis/<id>/impl/<foundry>/impl.patch`

If any is missing, stop and tell the human which generator to run
first (`/analyze-paper` or `/implement`).

CONTEXT (read-only):
- The Design document (passed as argument) — the authoritative spec.
- `analysis/<id>/analysis.md` — the originating analysis.
- `analysis/<id>/impl/<foundry>/impl.md` + `impl.patch` — the
  implementation under validation.
- Any other analyses the Design cites as supporting evidence (when
  named in `analysis/<id>/analysis.md` ✨ 핀 논문 대비 델타 or 🎯 관련
  Pillar / Decision).
- For `--foundry lerobot`:
  - `vendor/lerobot/policies/<base>/` (the base named in the impl
    guide) — `configuration_*.py`, `modeling_*.py`, `processor_*.py`.
    Read the actual functions the patch touches before judging
    signatures.
- `analysis/<id>/impl/<foundry>/test_*.py` — the impl's sibling smoke
  test (if present). The executable counterpart of `impl.patch`; §🧬
  runs it.
- `scripts/ensure-foundry-runtime.sh` — builds the executable runtime
  (full upstream checkout at the pinned commit + venv) on demand, prints
  the venv python on its last stdout line, exits non-zero (and tells you
  to degrade to static-only) when it cannot.
- `analysis/_TEMPLATE_VALIDATION.md` — the exact form the report must
  follow.
- `docs/STYLE.md` — §7 (Validation report) + §4.

Do NOT edit any file under `context/`, `vendor/`, the Design, the
originating analysis, or the impl guide/patch — those are immutable
inputs. This command writes only the validation report.

You do NOT run training, evaluation, or real-checkpoint inference. The
ONLY code you execute is (1) `git apply --check`, (2)
`bash scripts/ensure-foundry-runtime.sh <foundry>` to build the runtime,
and (3) the impl's sibling CPU smoke test under that runtime (§🧬). No
`pip install` by hand — the runtime script owns dependency setup. If the
runtime cannot be built, 🧬 is `skipped`, never fabricated.

TASK — produce this output (overwriting if it exists):

  - `analysis/<id>/validation/<foundry>.md` — Korean validation report.

The report is the deliverable. There is no manifest lifecycle to
graduate; the analysis track is fidelity-only.

PROCEDURE — five checks, in this order, each its own `##` section in
the report (📚 / 🔍 / 🧪 / 📐 fold into the static tier; 🧬 is the
execution tier):

A. 📚 문헌 대조.
   For each analysis the Design cites as supporting evidence (the
   originating `analysis/<id>/analysis.md` itself plus any other analyses
   named in its 🎯 관련 Pillar / Decision or ✨ 핀 논문 대비 델타
   sections), read it in full and decide whether the Design is:
     - 일치 — analysis directly supports the Design's claim. Quote one
       verbatim line from the analysis's §⚙️ 의사결정 함의 or §🔬 방법론.
     - 충돌 — analysis says something the Design contradicts. Quote
       the contradicting line.
     - 확장 — analysis is silent on this specific claim but consistent
       with it as an extension. Name the gap.
     - 무관 — analysis was cited but does not actually inform the
       Design. Flag as misclassification.

   Rule: at least one `일치` or `확장` row is required to mark this
   check `pass`. Any `충돌` row marks `fail`. Only-`무관` rows mark
   `partial`.

B. 🔍 패치 정합성.
   Re-run `git apply --check` against the current foundry tree
   (foundry may have been refreshed since `/implement` ran):

   ```bash
   cd /home/user/probe && git apply --check analysis/<id>/impl/<foundry>/impl.patch
   ```

   Record stdout/stderr verbatim. Zero exit → `pass`. Non-zero exit →
   `fail` and the report row carries the verbatim error.

C. 🧪 시그니처·하이퍼파라미터 일치.
   For every patched file under the foundry's code root (for lerobot:
   `vendor/lerobot/policies/<base>/`), read the actual function/class
   the patch touches and compare:
     - **함수/메서드 시그니처** — Does the patch's added call site or
       new argument match the signature in the foundry file? (If the
       patch adds a kwarg, does the function accept `**kwargs` or have
       it explicitly?)
     - **하이퍼파라미터 / 상수** — Does every numeric or string
       constant the Design or impl guide cites (verbatim per
       STYLE §4-1: `ε = 0.1`, `chunk_size = 50`, etc.) match
       what the patch actually sets? Constants named in the Design
       but absent from the patch → `partial`. EXCEPTION: a constant
       that belongs to a module classified `out-of-base-scope` (per
       impl.md §🧱 cover/exclude + §🪛) is NOT counted against this
       verdict — it is out of the patch's scope by design, tracked in
       §🔎 `out-of-base-scope` instead. Counting it would manufacture a
       permanent `partial` that drives endless inner steps the inner
       loop cannot resolve.
     - **import 경로** — Are new imports valid against the foundry
       tree? No fabricated module paths.

   `pass` only if every checked row matches. Any signature mismatch
   that would cause a runtime error is `fail`. Constants quoted in
   prose but missing in code are `partial`.

D. 📐 식·표 일치 (separate `##` section in the report).
   For every formula or table reference the Design or its cited
   analyses mention (e.g. `Eq. (4)`, `Table 3`), check that the patch
   either implements it (point at the corresponding hunk) or
   explicitly defers it to 🚧 in `impl.md`. Citations with no hunk
   and no 🚧 row are silent-skip — call them out as `partial` in the
   signature_check verdict (this section folds into 🧪 for the
   summary).

E. 🧬 실행 검증 (separate `##` section in the report).
   The static checks above prove the patch *diffs* correctly. This check
   proves it *runs*. Only applies when the impl ships a sibling smoke
   test (`analysis/<id>/impl/<foundry>/test_*.py`); if there is none,
   record `skipped — no sibling test` and move on (an in-place patch with
   no test cannot be executed — note it as a 🚧 for the foundry step to
   add one).

   Procedure (do exactly this; do not improvise other code execution):

   1. Build the runtime:

      ```bash
      cd /home/user/probe && py=$(bash scripts/ensure-foundry-runtime.sh <foundry>)
      ```

      Non-zero exit → record `🧬 skipped — <stderr first line>` (offline
      / install failure). The static verdicts stand; do NOT fail the
      validation on a missing runtime.

   2. Apply the patch to the runtime checkout, translating the vendored
      path prefix to the upstream layout (`vendor/<foundry>/` →
      `src/<foundry>/`). For `--foundry lerobot`:

      ```bash
      src=.foundry-runtime/<foundry>/src
      git -C "$src" apply -p3 --directory=src/lerobot \
          "$PWD/analysis/<id>/impl/<foundry>/impl.patch"
      ```

      Apply failure here (when `git apply --check` in §🔍 passed against
      the snapshot) means the snapshot and the upstream checkout have
      drifted — record `🧬 fail — patch did not apply to runtime` and
      cite the stderr.

   3. Run ONLY the sibling test, copying it into the checkout's `tests/`
      tree (so its `lerobot.*` imports resolve against the editable
      install):

      ```bash
      cp analysis/<id>/impl/<foundry>/test_*.py "$src/tests/"
      "$py" -m pytest "$src/tests/$(basename analysis/<id>/impl/<foundry>/test_*.py)" -q
      ```

      Record the pytest summary line verbatim (`N passed`, or the first
      failing assertion + traceback tail on failure).

   4. Restore the checkout so the runtime stays reusable:
      `git -C "$src" checkout -- . && git -C "$src" clean -fdq tests/`.

   Verdict: `pass` (all tests green) / `fail` (apply or any test fails) /
   `skipped` (no test, or runtime unbuildable). A `fail` is a real defect
   — the patch claims a behaviour the code does not exhibit; cite the
   failing assertion. Record the verbatim pytest output in the report.

F. ⚖️ 종합 판정.
   One `##` section summarising the four verdicts (literature ·
   patch_consistency · signature_check · execution). Write one line
   summarising whether the analysis can rely on this implementation:
     - All `pass` (🧬 `pass` or `skipped`) → "이 foundry 의 구현은
       Design 과 정합하며 실행 검증을 통과합니다." (🧬 skipped 이면
       "(실행 검증은 런타임 미가용으로 생략)" 을 덧붙입니다.)
     - Any `fail` (static OR 🧬) → "이 foundry 의 구현은 정합하지
       않습니다 — <어떤 체크가 어떤 사유로 실패했는지>."
     - Mixed `pass`/`partial` (no `fail`) → "이 foundry 의 구현은
       부분적으로 정합합니다 — <partial 항목>."

   The report has no status to graduate — the verdict is the
   deliverable.

G. 🔎 §🚧 분류 (separate `##` section in the report).
   Read `impl.md §🚧 미해결 / 잠정` end-to-end. Classify EVERY row into
   exactly one of five buckets. This is the single source of truth that
   `/reproduce-paper` reads to choose the next action — fabricating
   even one row poisons the outer loop, so honesty here is critical.

   The base scope is NOT objective — it is the foundry agent's own §A
   choice (which single base, which of the paper's policies/modules it
   covers). So `out-of-base-scope` must never be a self-serving escape:
   it is valid ONLY when `impl.md §🧱` explicitly declares which paper
   modules the base covers vs. excludes, and the row cites that
   declaration. If `§🧱` carries no cover/exclude declaration, you may
   NOT use `out-of-base-scope` — fall through to the paper-* buckets.

   Buckets (in priority order; pick the first that applies):

   - `vendor-resolved` — the foundry already encodes an equivalent
     constant or default. Cite a vendor `file:line` whose value the
     next foundry round can lift directly. Example for `--foundry
     lerobot`: `vendor/lerobot/policies/<base>/configuration_<base>.py:
     LNN` carries the field. Once promoted, the row moves from §🚧 to
     §🧪 in the next round's impl.md.
   - `out-of-base-scope` — the paper AND the Design both fully specify
     the item, but it belongs to a module/policy the chosen base does
     not cover (e.g. a tactile CAE encoder or a standalone LSTM policy
     when the base maps only the unified arm-hand policy onto `pi0`).
     Cite the `impl.md §🧱` cover/exclude declaration. Record it in
     `§🪛` as 신규-미구현, NOT as a §🚧 loop-driver; `/reproduce-paper`
     treats it as an honest defer (no outer, no inner). This bucket
     ranks ABOVE `paper-extractable` on purpose: re-extracting the
     Design (the outer step) cannot help an item that has no insertion
     point in this base, so routing it to `paper-extractable` would
     spend an outer round that changes no patch — the exact symptom the
     reproduce-loop zero-patch-delta guard flags.
   - `paper-extractable §X.Y` — the paper body has the information,
     but the existing Design captured only a sketch. Cite the specific
     §X.Y (or table / equation number) where the missing detail lives.
     `/reproduce-paper` 's outer step will pass these §X.Y tokens to
     `/analyze-paper --focus` for re-extraction.
   - `paper-silent-defaultable` — paper body is silent, but a defensible
     default exists (vendor convention, established practice, or
     1-line argument). Next foundry round promotes the row to a patch
     hunk with a 1-line `# NOTE: paper §X silent, default <v> chosen —
     reason: ...` comment.
   - `paper-silent-experimental` — paper body silent AND no defensible
     default. Resolution requires an external experiment / ablation /
     author contact. Stay in §🚧 honestly; surface as
     `stable_partial` termination reason.

   No force-fit. If a row honestly fits NONE of the five buckets, do
   NOT shoehorn it into the nearest one to reach a clean termination —
   that is the misclassification failure mode this taxonomy guards
   against. Instead leave the row in §🚧, tag it `taxonomy-gap` in the
   bucket cell with a one-line reason, and add a `taxonomy-gap` line to
   the machine footer (below). `/reproduce-paper` treats any
   `taxonomy-gap` row as `hold_and_report` rather than silent
   convergence.

   Run zero-state every round. Do NOT inherit the prior round's table.
   The §C stability check on `<!-- ANALYSIS_BUCKETS -->` set equality
   catches honest fixed points; an inherited table would smuggle prior
   misclassifications into later rounds.

   Output the section in the form prescribed by `_TEMPLATE_VALIDATION.md` §🔎.
   The machine-readable footer
   (`<!-- ANALYSIS_BUCKETS:START --> ... <!-- ANALYSIS_BUCKETS:END -->`)
   is mandatory — `/reproduce-paper` parses it verbatim:

     - `vendor-resolved:` comma-separated §🚧 row numbers (empty if
       none).
     - `paper-extractable:` row numbers.
     - `paper-silent-defaultable:` row numbers.
     - `paper-silent-experimental:` row numbers.
     - `out-of-base-scope:` the `§🪛` row numbers of the excluded
       modules (these live in `§🪛`, not `§🚧`); list them in the §🔎
       table too, citing their §🪛 entry. Empty if none.
     - `focus-hint:` sorted, comma-separated, deduplicated `§X.Y`
       tokens from the `paper-extractable` rows. Use `§` (U+00A7) to
       match `docs/STYLE.md` §4-1 verbatim quotation. Empty if no
       `paper-extractable` row.

   If any row was tagged `taxonomy-gap` (above), add one more line
   `taxonomy-gap:` with those row numbers. `/reproduce-paper` reads it
   verbatim and halts on a non-empty value.

   Also append a `🔎 §🚧 분류` row to the meta header summary
   (`<vendor-resolved> N / <paper-extractable> N / ...`) — keeps the
   validation table's top-of-file glance accurate.

   `partial` / `fail` verdicts on §🧪 / §📐 do not by themselves drive
   the bucket choice; the buckets are about §🚧 items specifically. A
   `🧪 partial` row whose underlying gap is also a `vendor-resolved`
   §🚧 item is normal — both surface, both are addressed by the next
   round.

HARD RULES:
- Code execution is limited to: `git apply --check`, the runtime
  builder `scripts/ensure-foundry-runtime.sh`, and the impl's sibling
  CPU smoke test (§🧬). No training, no real-checkpoint inference, no
  manual `pip install`, no model-weight load. If a deeper check would
  require those, leave it as 🚧 — never run a real training/eval to
  resolve an validation row.
- No edits under `context/`, `vendor/`. No edits to the Design,
  originating analysis, or impl files. The only writable file in
  this command is the validation report.
- Every `fail` row records the command + stderr verbatim. Every
  `partial` row names the specific missing-or-misaligned item.
- Single Korean document. KO-only filename.
- Emoji/header system per `docs/STYLE.md` §7.
- Honesty over completeness — `partial` is a normal outcome. A
  fabricated `pass` is far worse than an honest `partial`.

---

GIT — after the report is written:

  git add analysis/<id>/validation/<foundry>.md
  git commit -m "validation: <id> on <foundry>"
  git push origin HEAD:main

Do NOT stage `analysis/INDEX.md` and do NOT run
`scripts/refresh-analysis-index.py` from this prompt. The index
(including the validation bucket-count column) is regenerated
post-merge on `main` by
`.github/workflows/refresh-analysis-index.yml` so that parallel
validation runs cannot collide on the same generated block (see
`CLAUDE.md` "Automatically-maintained indexes"). Local manual
regeneration is still safe and idempotent if needed for ad-hoc
inspection.

Standard rebase-and-retry / network-retry rules as in other PROBE
prompts. Never `--no-verify`, never force-push.
