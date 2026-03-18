# Memory Index

## Feedback
- [feedback_ticket_workflow_order.md](feedback_ticket_workflow_order.md) — CEO/Eng reviews should happen before detailed ticket specs, not after
- [feedback_no_separate_design_docs.md](feedback_no_separate_design_docs.md) — Put design context in project description, requirements in ticket descriptions, no separate design docs
- [feedback_subagent_permissions.md](feedback_subagent_permissions.md) — Background subagents need mode: "acceptEdits" to avoid permission denial on Edit/Write/Bash
- [feedback_lead_no_code.md](feedback_lead_no_code.md) — When orchestrating agents, lead must never write code directly — always delegate, even for trivial fixes
- [feedback_one_at_a_time.md](feedback_one_at_a_time.md) — Present acceptance criteria and decisions one at a time, not batched

## Reference
- [reference_supabase_project.md](reference_supabase_project.md) — Supabase MCP is under project "nextbest", tool prefix mcp__claude_ai_supabase_nextbest__
- [reference_railway_pipeline.md](reference_railway_pipeline.md) — Pipeline deployed on Railway, uses uv sync --locked, must update uv.lock when changing deps
- [reference_railway_cli.md](reference_railway_cli.md) — Railway CLI is installed, use branch environments for feature branches not production
- [reference_pipeline_dev_setup.md](reference_pipeline_dev_setup.md) — Pipeline worktree setup requires --extra dev and --python 3.12 (pyroaring build fails on 3.14)
