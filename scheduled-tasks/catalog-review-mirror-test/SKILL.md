---
name: catalog-review-mirror-test
description: One-off rehearsal of the catalog-review routine against the LOCAL Supabase mirror, covering the NEX-807 new_tag and new_brand lanes. Report-only: writes research into mirror dossiers, never applies, never touches production.
---

Third rehearsal of the `catalog-review` routine, **LOCAL Supabase mirror only**, focused on ONE question: does the `new_brand` retry path actually recover a row whose products our own earlier research left with no aliases? You have no context from any other session — that is the point.

Background (facts, not instructions to re-derive): an earlier rehearsal struck every alias off the SKUs of two brands, **Plum** (`1c65c12e-c49f-4674-bddf-6cbdc3fec6b4`) and **Ksecret** (`3e09efdb-e900-4aed-846e-a5cec67e3375`), using guidance that has since been corrected. The brand prompt now has a **step 3b retry branch** for exactly this shape. Both rows are currently re-researchable.

## Where the code is

Run every helper command from `/Users/kayleigh/dev/nextbest/.worktrees/nex-807-tag-brand-lanes/frontend` — the NEX-807 worktree, NOT the main checkout. Authority: that worktree's `.claude/skills/catalog-audit/SKILL.md` (read it first — the `new_brand` plain-language table, Step 0, Step 1's new_brand prompt **including step 3b**, Step 2's write rules and within-lane duplicate pass, Step 3's digest, Step 4's read-back dedupe and display rules) and `.claude/skills/catalog-audit/routine-prompt.md`.

## 🚨 Mirror only, report-only

- Every command passes `--env .env.local`; confirm `/usr/bin/grep -a SUPABASE_URL frontend/.env.local` shows `127.0.0.1` first, else STOP.
- **Never `--env .env.prod`, never `--base-url https://www.nextbest.one`, never `apply` without `--dry-run`**, never a status change.
- `grep` is ugrep — use `/usr/bin/grep -a` or `rg`. Never wrap a command in `timeout` (macOS has none). Capture exit codes without piping through `tail`.
- Scratchpad `/private/tmp/catalog-review-mirror-test3/`. A dev server for the mirror runs at `http://localhost:3807`. No Linear comment — your reply is the report.

## Steps

1. `counts --env .env.local`; keep the JSON line.
2. **Default pull, limit 40** (the retry rows sit behind the oldest-first slice; a smaller limit misses them):
   `list --lane new_brand --status pending --limit 40 --out /private/tmp/catalog-review-mirror-test3/queue-new_brand.json --env .env.local`
   Record every line it prints, especially `re-researchable (brand-struck no_attach): N — <ids>`. Confirm Plum and Ksecret are among the cards, and quote their `skus[]` blockers and `excluded_aliases` as they stand BEFORE research.
3. **Research.** Dispatch ONE `Agent` (`subagent_type: "general-purpose"`, `model: "opus"`, `run_in_background: true`) over a batch file holding **only the two retry cards** plus at most 4 other cards from the pull, with the new_brand lane prompt from SKILL.md **verbatim**, a brands file written from the mirror (`psql postgresql://postgres:postgres@127.0.0.1:54322/postgres -X -A -t -c "select coalesce(json_agg(json_build_object('id',id,'name',name,'aliases',aliases) order by name),'[]') from brands" > /private/tmp/catalog-review-mirror-test3/brands.json`), and a distinct output path. Do not tell it which answer to reach and do not hand-edit its findings; whether step 3b works is the measurement.
4. Consolidate + validate (Step 2), including the within-lane duplicate pass reported in the required form. Then `write-research ... --env .env.local`; record `written / skipped / needs_enrichment`.
5. **Re-list** (`list --lane new_brand --researched-only --out .../researched-new_brand.json --env .env.local`) and answer explicitly, per brand:
   - did any SKU that was `no_attach` become **sendable**?
   - what does the row's `no_attach_retry_at` / `no_attach_retry_attempts` look like now (read them with `psql` on the mirror), and does that match the documented spend rule for the finding the agent actually produced?
6. **Dry run** the approvable classes: build `decisions-new_brand.json` per Step 4 (including its read-back dedupe pass), then `apply --queue .../researched-new_brand.json --file .../decisions-new_brand.json --base-url http://localhost:3807 --env .env.local --dry-run`. Quote the `authenticated as` line, each `bundle-approve` body's brand + SKU count + the aliases each SKU would get, and every `skipped` row with its reason.
7. **Report** in Step 3's digest format, then a short section headed **"Did the retry work?"** answering yes/no with the evidence above, and **"Prompt feedback"** — anything ambiguous, wrong, or contradicting the helper, quoting the wording that misled you. Specifically: was step 3b findable and usable at the moment you needed it, and did anything in the ordered steps still push you toward `undecided` on those two rows?

## Failure handling

Any helper command exiting non-zero: stop, put the command and its error in the report, reply. Never invent findings for a failed agent batch.