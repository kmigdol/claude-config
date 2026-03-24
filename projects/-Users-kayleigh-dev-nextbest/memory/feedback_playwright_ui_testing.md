---
name: feedback_playwright_ui_testing
description: UI layout changes must include Playwright e2e tests with boundingBox() assertions, TDD-style
type: feedback
---

UI layout changes require Playwright e2e tests that verify rendered layout using boundingBox() checks.

**Why:** A compact card feature shipped with the score badge and favorite button overflowing the card boundary — unit tests didn't catch it because they test DOM structure, not visual rendering. Playwright boundingBox() catches layout overflow, spacing regressions, and responsive issues.

**How to apply:** For any frontend change affecting layout, spacing, or visual behavior: write a Playwright e2e test FIRST (TDD), confirm it fails, fix the issue, confirm it passes. Test both desktop (1280x800) and mobile (375x812) viewports. Tests go in `frontend/e2e/`.
