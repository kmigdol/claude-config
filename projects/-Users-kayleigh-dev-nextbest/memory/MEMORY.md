# Memory Index

## Feedback
- [feedback_ticket_workflow_order.md](feedback_ticket_workflow_order.md) — CEO/Eng reviews should happen before detailed ticket specs, not after
- [feedback_no_separate_design_docs.md](feedback_no_separate_design_docs.md) — Put design context in project description, requirements in ticket descriptions, no separate design docs
- [feedback_subagent_permissions.md](feedback_subagent_permissions.md) — Background subagents need mode: "acceptEdits" to avoid permission denial on Edit/Write/Bash
- [feedback_lead_no_code.md](feedback_lead_no_code.md) — When orchestrating agents, lead must never write code directly — always delegate, even for trivial fixes
- [feedback_one_at_a_time.md](feedback_one_at_a_time.md) — Present acceptance criteria and decisions one at a time, not batched
- [feedback_check_ci_after_main.md](feedback_check_ci_after_main.md) — Always verify CI passes on GitHub after pushing to main, don't trust local checks alone
- [feedback_vercel_stale_cache.md](feedback_vercel_stale_cache.md) — Vercel preview builds can use stale .next cache causing missing data — may need clean rebuild
- [feedback_large_tickets_slow.md](feedback_large_tickets_slow.md) — Split large tickets into smaller vertical slices, add e2e tests for auth flows, batch UI feedback
- [feedback_playwright_ui_testing.md](feedback_playwright_ui_testing.md) — UI layout changes must include Playwright e2e tests with boundingBox() assertions, TDD-style

## Project
- [project_trust_value_prop.md](project_trust_value_prop.md) — Trust (not just time savings) is the core value prop — users distrust influencers, affiliate monetization must not erode this
