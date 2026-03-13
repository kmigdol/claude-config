---
name: creating-linear-tickets
description: Use when turning an idea or feature request into Linear tickets — orchestrates brainstorming, CEO review, engineering review, and ticket creation with acceptance criteria
---

# Creating Linear Tickets

## Overview

Turn ideas into well-scoped Linear tickets through structured review. Orchestrates: brainstorm → CEO review → Eng review (architecture) → scope assessment → Linear creation.

Every ticket created by this skill has validated scope, reviewed architecture, clear acceptance criteria, and a linked design document — so `starting-linear-ticket` can execute without re-discovering context.

**Announce at start:** "Using creating-linear-tickets to turn this idea into actionable tickets."

## Required Input

An idea, feature request, bug report, or initiative. Can be:
- A verbal description ("I want to add Google Calendar integration")
- A Notion doc reference
- A Linear project/milestone to break down
- A bug report or user feedback

## Fast Path — Small, Well-Scoped Tickets

**Not every ticket needs the full workflow.** Skip brainstorming and reviews when ALL of these are true:

- The problem is obvious and well-understood (e.g., a specific bug with a known fix)
- The scope is already tight — one change, one area of the codebase
- There's no design ambiguity — no "should we do A or B?" questions
- The user has clearly articulated what they want

**Fast path:** Read the relevant code to understand the current state → create a well-formed ticket with problem statement, affected code, solution sketch, and acceptance criteria. No brainstorming, no CEO review, no Eng review.

**Examples of fast-path tickets:**
- "Day boundary uses UTC instead of local time" — it's a bug, the fix is clear
- "Add loading spinner to the save button" — tiny UI improvement, no ambiguity
- "Rename `foo` to `bar` across the codebase" — mechanical refactor

**Examples that need the full workflow:**
- "Add Google Calendar integration" — multiple approaches, scope unclear
- "Redesign the daily routine flow" — requires exploring alternatives
- "Add a weekly review feature" — new concept, needs CEO + Eng review

**When in doubt, ask:** "This seems well-scoped enough for a quick ticket. Want me to run the full workflow or just create the ticket?"

## Workflow (Full)

```dot
digraph workflow {
    rankdir=TB;
    brainstorm [label="1. Brainstorm", shape=box];
    ceo [label="2. CEO Review\nEXPAND → HOLD → REDUCE", shape=box];
    eng [label="3. Eng Review\n(Architecture)", shape=box];
    scope [label="4. Scope Assessment", shape=diamond];
    single [label="5a. Create Single Ticket", shape=box];
    project [label="5b. Create Project + Tickets", shape=box];
    doc [label="6. Create Design Document", shape=box];
    link [label="7. Link Everything", shape=box];

    brainstorm -> ceo -> eng -> scope;
    scope -> single [label="small"];
    scope -> project [label="large"];
    single -> doc;
    project -> doc;
    doc -> link;
}
```

### Step 1: Brainstorm

**REQUIRED SUB-SKILL:** Invoke `superpowers:brainstorming`

Provide the idea as context. Brainstorming will:
- Ask clarifying questions one at a time
- Explore 2-3 approaches with trade-offs
- Present a design incrementally for validation

**Do NOT save a design doc yet** — the design will be refined by the review phases.

### Step 2: CEO Review

**REQUIRED SUB-SKILL:** Invoke `plan-review-ceo`

Pass the brainstorming output. The CEO review runs EXPAND → HOLD → REDUCE and produces:
- **Building now** — what goes into tickets
- **Building later** — deferred with rationale
- **Not building** — explicitly killed

### Step 3: Eng Review (Architecture)

**REQUIRED SUB-SKILL:** Invoke `plan-review-eng` in **planning mode**

Pass the validated scope from CEO review. The Eng review produces:
- ASCII architecture diagram
- File list (create/modify)
- Failure modes
- Dependency graph for ticket ordering
- "What already exists" section

### Step 4: Scope Assessment

Auto-detect whether this is a single ticket or project with multiple tickets:

| Signal | Single ticket | Project + tickets |
|--------|--------------|-------------------|
| Architecture touches | 1-2 areas | 3+ distinct areas |
| "Building now" items | 1-3 related | 4+ or separable |
| Natural ticket count | 1 | 2+ vertical slices |
| Has "Building later" list | No or trivial | Yes, meaningful |

**Always ask to confirm** before creating: "This looks like [single ticket / a project with N tickets]. Sound right?"

### Step 5a: Create Single Ticket

```
mcp__linear-server__save_issue with:
- title: Descriptive, action-oriented
- description: See ticket template below
- teamId: <team-id>  # Look up with list_teams
- stateId: <backlog-state-id>  # Look up with list_issue_statuses
- priority: 1-4 based on discussion
- labelIds: [Feature | Bug | Improvement]  # Look up with list_issue_labels
```

### Step 5b: Create Project + Tickets

1. **Create or find project** — Use existing milestone if applicable, otherwise create via `mcp__linear-server__save_project`
2. **Create vertical-slice tickets** — Each delivers complete user value:
   - Include frontend + backend + tests in a single ticket
   - Order by dependency graph from Eng review
   - Each ticket references the design document
3. **Create "Building later" tickets** — Separate backlog tickets with rationale preserved from CEO review
4. **Add dependency notes** — In ticket descriptions: "Depends on: PROJ-XX" where ordering matters

### Step 6: Create Design Document

Create a Linear document with the full design:

```
mcp__linear-server__create_document with:
- title: "Design: <feature name>"
- content: See design doc template below
```

### Step 7: Link Everything

- Add design document link to each ticket's description
- If project was created, ensure all tickets are linked to it
- Report back: list of created tickets with IDs and titles

## Ticket Description Template

```markdown
## Problem
<Problem statement from CEO review — why are we building this?>

## Solution
<Architecture summary from Eng review — how does it work?>

## Architecture
<ASCII diagram from Eng review>

## Acceptance Criteria
- [ ] <Specific, testable condition derived from "Building now" list>
- [ ] <Each criterion maps to a verifiable outcome>
- [ ] <Include both happy path and key edge cases>

## Design Document
<Link to Linear document>

## Dependencies
<"Depends on: PROJ-XX" if applicable, or "None">

## Not In Scope
<Items explicitly deferred or cut, from CEO review>
```

## Design Document Template

```markdown
# Design: <Feature Name>

## Problem Statement
<From CEO review — validated problem, who benefits, what happens if we don't build>

## Scope Decisions
### Building Now
<Items and rationale>

### Building Later
<Deferred items with rationale — these become backlog tickets>

### Not Building
<Killed items with rationale>

## Architecture
<ASCII diagram from Eng review>

### Components
<What's created, what's modified, what's reused>

### Data Flow
<How data moves through the system>

### Failure Modes
<From Eng review — each new codepath's realistic failure scenario>

## Ticket Breakdown
<List of tickets created, with IDs, in dependency order>
```

## Common Mistakes

### Creating tickets without acceptance criteria
- **Problem:** Executor doesn't know what "done" looks like
- **Fix:** Every ticket gets specific, testable acceptance criteria derived from the review phases

### Horizontal instead of vertical ticket slicing
- **Problem:** "Create API route", "Create component", "Create hook" — none deliver value alone
- **Fix:** Each ticket is a vertical slice: backend + frontend + tests = usable feature

### Skipping reviews for "obvious" features
- **Problem:** Assumptions go unchallenged, scope creeps during implementation
- **Fix:** Run the full workflow. CEO review catches bad assumptions, Eng review catches architectural issues.

### Not preserving rationale for deferred items
- **Problem:** "Building later" items lose context, become meaningless backlog entries
- **Fix:** Include WHY it was deferred and WHAT would trigger building it

## Red Flags
- "This is just one quick ticket, we don't need all this"
- "The acceptance criteria are obvious"
- "Let me just create the tickets and start coding"
- "We can figure out the architecture during implementation"

**All of these mean: Run the workflow. Cheap questions now save expensive rework later.**
