---
name: Large tickets cause slow agents
description: Split large tickets into smaller vertical slices, add e2e tests for auth flows, batch UI feedback
type: feedback
---

NEX-31 (User Accounts) was too large — auth + profiles + favorites + personalization + analytics in one ticket. The agent took a long time due to cascading runtime bugs that unit tests couldn't catch.

**Why:** Runtime issues (session cookie deadlock, Vercel cache, RLS silent failures) required repeated build/test/debug cycles. Scope additions mid-flight (3-tier sorting, bigger heart, dry skin, use_caution) added more cycles. 153 unit tests passed but the app was broken in production.

**How to apply:**
- Split large features into 3-4 smaller vertical slices (e.g., auth → profile → favorites → personalization as separate tickets)
- Add Playwright e2e tests for integration-heavy features like auth flows — unit tests alone can't catch cookie/session/RLS issues
- Batch UI feedback into a single pass instead of sending one-at-a-time while agent is debugging
- Agents should report blockers proactively instead of silently rebuilding
- SSG apps require full rebuilds to test — minimize rebuild cycles by grouping changes
- **Push back on scope creep:** When the user requests changes during an active PR, the lead should assess whether they belong in the current ticket or a follow-up. New features (3-tier sorting, caution badges) should be follow-up tickets, not mid-flight additions. Quick fixes (bigger icon, missing option) are fine. Default to creating a follow-up ticket and asking the user rather than sending more work to the agent.
- **Don't over-delegate quick tweaks:** The delegation round-trip (send message → agent reads → edits → checks → pushes → reports) takes 5+ minutes even for 1-line changes. For rapid UI iteration (bigger icon, reorder elements, CSS tweaks), the lead should do them directly or spawn a fast subagent — not route through a long-running agent. Reserve delegation for multi-file features and autonomous work.
