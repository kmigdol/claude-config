---
name: Check CI after pushing to main
description: Always verify CI passes on GitHub after pushing directly to main — don't trust local checks alone
type: feedback
---

After pushing commits directly to main, always check that CI passes on GitHub using `gh run list` / `gh run view --log-failed`. Local checks can miss issues (different ruff versions, missing env vars, formatting differences).

**Why:** Multiple consecutive CI failures on main from pushes that passed locally but failed in CI (unused imports, formatting, env var assumptions). Each fix required another push, compounding the problem.

**How to apply:** After every `git push` to main, run `gh run list --repo <repo> --limit 1` and wait for the result. If it fails, check `gh run view <id> --log-failed` and fix before moving on. Don't assume "it passed locally so it's fine."
