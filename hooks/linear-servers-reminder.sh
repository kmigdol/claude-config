#!/bin/sh
# SessionStart hook: inject the Linear MCP server-resolution rule into context.
# Two Linear servers exist (mcp__linear-server__* and a UUID-prefixed claude.ai
# connector). The startup "needs authentication" reminder describes only the
# first; the connector has been reported unavailable in error 6+ times.
cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"LINEAR MCP RULE (SessionStart hook, ~/.claude/hooks/linear-servers-reminder.sh): Linear is wired TWICE — `mcp__linear-server__*` and a UUID-prefixed claude.ai connector (`mcp__5afa51ff-6015-498e-9e18-a1d1d62866c2__*`, same tools). A system reminder that `linear-server` needs authentication says NOTHING about the connector. Before ever writing 'Linear is unavailable/unauthenticated', run ToolSearch with BARE tool verbs and no product name: `save_issue get_issue list_issues save_comment`. Searching for the word 'linear' (`+linear ...`, `select:mcp__linear-server__...`) finds nothing and proves nothing. Use whichever prefix the search returns for every mcp__linear-server__* call named in CLAUDE.md or the skills. Only an empty bare-verb search means Linear is unavailable, and re-run it at the moment of the write — the connector can attach mid-session."}}
JSON
