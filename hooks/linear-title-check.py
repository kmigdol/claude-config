#!/usr/bin/env python3
"""PreToolUse gate on Linear save_issue: enforce the ticket-title rule.

The rule (see ~/.claude/CLAUDE.md "Ticket Titles" and the creating-linear-tickets
skill): a title is ONE imperative sentence naming the change, in concrete nouns,
with no trailing em-dash clause explaining or justifying it.

This checks only the mechanical failures — the ones that are decidable from the
string. Judging whether the verb names a real outcome stays with the model; the
block message reminds it to apply that test.

Exit 0  = title fine (or no title in this call), tool proceeds.
Exit 2  = blocked; stderr goes back to the model, which rewrites and retries.
"""

import json
import re
import sys

MAX_LEN = 100

# " — ", " – ", " - " with spaces on both sides. Hyphenated words ("new-brand",
# "precision/recall") have no surrounding spaces, so they don't trip this.
DASH_CLAUSE = re.compile(r"\s[—–-]\s")

LEADING_ARTICLE = re.compile(r"^(a|an|the)\s", re.IGNORECASE)
LEADING_GERUND = re.compile(r"^\w+ing\s", re.IGNORECASE)
# "Product variants: link …" — an Area: prefix is legitimate, so only inspect
# the part after a leading colon when one appears early in the title.
AREA_PREFIX = re.compile(r"^[^:]{1,40}:\s*")

RULE = """The ticket-title rule (~/.claude/CLAUDE.md "Ticket Titles"):

  ONE imperative sentence naming the change, in concrete nouns.
  Optional "Area:" prefix. NO trailing em-dash clause explaining it.

Calibration:
  - "Cut daily pipeline cron over from Railway to Prefect schedule"
  - "Stop a killed run from skipping the next day's pipeline"
  - "Product variants: link distinct sibling SKUs into a family + \"Other variants\" on product pages"

Also check the part this hook can't: would a user or the business notice this
verb's effect? "Emit a completion marker" / "Add a column" / "Coalesce the
handlers" are implementation steps, not outcomes — if that's the honest verb,
this is a task inside an existing ticket, not a ticket (Gate 1).

The symptom goes in the ## Problem section, at full detail. Not the title."""


def violations(title: str) -> list[str]:
    found = []

    if DASH_CLAUSE.search(title):
        found.append(
            'Contains an explanatory dash clause ("<change> — <the symptom it '
            "fixes>\"). Cut everything from the dash onward; that content belongs "
            "in ## Problem. If the verb can't stand alone without it, fix the verb."
        )

    if len(title) > MAX_LEN:
        found.append(
            f"{len(title)} characters, over the {MAX_LEN} limit. Length almost "
            "always comes from explaining rather than naming the change."
        )

    body = AREA_PREFIX.sub("", title)
    if LEADING_ARTICLE.match(body):
        found.append(
            'Starts with an article ("A …" / "The …"), which reads as a symptom '
            "description of the world we're leaving rather than the change. Lead "
            "with an imperative verb."
        )
    elif LEADING_GERUND.match(body):
        found.append(
            'Starts with a gerund ("Approving …", "Renaming …"), which describes '
            "current behavior rather than naming the change. Lead with an "
            "imperative verb."
        )

    return found


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # never block on a payload we can't parse

    title = (payload.get("tool_input") or {}).get("title")
    if not isinstance(title, str) or not title.strip():
        return 0  # updates that don't touch the title

    found = violations(title.strip())
    if not found:
        return 0

    print(
        "Ticket title rejected:\n\n  "
        + title.strip()
        + "\n\n"
        + "\n".join(f"  {i}. {v}" for i, v in enumerate(found, 1))
        + "\n\n"
        + RULE
        + "\n\nRewrite the title and call save_issue again.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
