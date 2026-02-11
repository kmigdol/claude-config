---
name: testing-langgraph-backend
description: Use when you need to test a LangGraph backend, verify tools work, or debug agent behavior
---

# Testing LangGraph Backend

## Overview

Test LangGraph backends using the right method for your scenario: direct invocation for quick checks, dev server + API for integration testing.

**Core principle:** Match testing method to what you need to verify.

**Recommended approach:** Create automated test scripts that send HTTP requests to the dev server.

## When to Use

**Use this skill when:**
- Testing new tools you just implemented
- Verifying agent behavior after changes
- Debugging tool failures
- Validating integration with external services (Supabase, APIs)

**Key principle:** Thorough testing uses multiple methods. Start simple, progress to integration.

## Testing Workflow for New Tools

**Follow this progression for new tool implementations:**

1. **Direct invocation** - Verify tool logic works (smoke test)
2. **Dev server + API** - Verify agent integration (automated)
3. **Studio** (optional) - Interactive debugging if needed

**Don't stop at step 1.** Direct testing only verifies the tool function, not agent behavior.

**Prefer automated API tests over manual Studio testing** - they're repeatable and catch regressions.

## Testing Methods

### Method 1: Direct Tool Invocation

**When:** Quick smoke test, verify tool logic works

**Steps:**
```bash
cd <backend-directory>
source .venv/bin/activate  # or venv/bin/activate
python
```

```python
from src.tools import your_tool

# Test single tool
result = your_tool.invoke({"param": "value"})
print(result)

# Verify structure
assert "expected_key" in result
```

**Advantages:** Fast, no server needed, good for debugging
**Limitations:** Doesn't test agent integration or streaming

### Method 2: Dev Server + API Requests (RECOMMENDED)

**When:** Test agent flow, tool integration, or end-to-end behavior

**This is the primary testing method** - automated, repeatable, catches regressions.

**Steps:**

1. **Start dev server in background:**
```bash
cd <backend-directory>
source .venv/bin/activate
langgraph dev
```

Server starts at `http://127.0.0.1:2024` and runs in background.

2. **Create test script:**
```python
#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://127.0.0.1:2024"

def test_tool_integration(query):
    """Send query and verify tool was called."""
    # Create thread
    response = requests.post(f"{BASE_URL}/threads", json={})
    thread_id = response.json()["thread_id"]

    # Send message (streaming)
    response = requests.post(
        f"{BASE_URL}/threads/{thread_id}/runs/stream",
        json={
            "assistant_id": "agent",  # Default agent ID for langgraph.json
            "input": {"messages": [{"role": "user", "content": query}]},
        },
        stream=True
    )

    # Extract tool calls from streaming response
    tool_calls = []
    for line in response.iter_lines():
        if not line:
            continue
        line_str = line.decode('utf-8')
        if not line_str.startswith('data: '):
            continue
        data_str = line_str[6:]  # Remove 'data: ' prefix
        if data_str.strip() == "[DONE]":
            continue

        try:
            data = json.loads(data_str)
            # Check for tool calls in AI messages
            if isinstance(data, dict) and "messages" in data:
                for msg in data["messages"]:
                    if msg.get("type") == "ai" and "tool_calls" in msg:
                        for tc in msg["tool_calls"]:
                            tool_calls.append(tc["name"])
                            print(f"🔧 Tool called: {tc['name']}")
                            print(f"   Args: {tc.get('args')}")
        except json.JSONDecodeError:
            continue

    return tool_calls

# Test
query = "What did creators say about retinol?"
tools = test_tool_integration(query)
assert "your_tool_name" in tools, f"Expected tool not called. Called: {tools}"
print("✅ Test passed!")
```

3. **Run test:**
```bash
python test_your_tool.py
```

**Advantages:**
- Automated and repeatable
- Tests real agent behavior with streaming
- Easy to verify tool calls and responses
- Can be committed for regression testing

**Limitations:**
- Requires server running
- More setup than direct invocation
- Server must be restarted if code changes

### Method 3: LangSmith Studio (OPTIONAL)

**When:** Manual exploration, interactive debugging (use sparingly)

**Note:** Prefer automated API tests (Method 2) for most testing. Studio is useful for one-off exploration but not repeatable.

**Steps:**

1. Start dev server (if not running):
```bash
langgraph dev
```

2. Open LangSmith Studio (URL printed in terminal):
```
🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

3. Use the UI to:
   - Start conversations
   - Inspect tool calls and results
   - View agent reasoning
   - Test edge cases interactively

**Advantages:** Visual, interactive, great for one-time exploration
**Limitations:** Manual, not repeatable, not automatable, can't commit tests

## Common Scenarios

### Scenario 1: Testing New Tool

**Goal:** Verify tool works correctly in isolation AND with agent

**Method:** Direct invocation → Dev server + API test (both required)

**Step 1: Direct test (smoke test)**
```python
from src.tools import cite_videos
result = cite_videos.invoke({"video_ids": ["7396945500139687175"]})
assert "citations" in result
assert len(result["citations"]) > 0
```

**Step 2: Integration test (required, not optional)**
```bash
# Terminal 1: Start dev server
cd <backend-directory>
source .venv/bin/activate
langgraph dev  # Leave running
```

```python
# Terminal 2: Create test_cite_videos_e2e.py
import requests
import json

BASE_URL = "http://127.0.0.1:2024"

# Create thread
response = requests.post(f"{BASE_URL}/threads", json={})
thread_id = response.json()["thread_id"]

# Send test query
query = "Analyze retinol videos and cite your sources"
response = requests.post(
    f"{BASE_URL}/threads/{thread_id}/runs/stream",
    json={
        "assistant_id": "agent",
        "input": {"messages": [{"role": "user", "content": query}]},
    },
    stream=True
)

# Verify cite_videos was called
tool_calls = []
for line in response.iter_lines():
    if not line:
        continue
    line_str = line.decode('utf-8')
    if line_str.startswith('data: '):
        try:
            data = json.loads(line_str[6:])
            if isinstance(data, dict) and "messages" in data:
                for msg in data["messages"]:
                    if msg.get("type") == "ai" and "tool_calls" in msg:
                        tool_calls.extend([tc["name"] for tc in msg["tool_calls"]])
        except:
            pass

assert "cite_videos" in tool_calls, f"cite_videos not called! Called: {tool_calls}"
print("✅ cite_videos integration test passed")
```

```bash
# Run test
python test_cite_videos_e2e.py
```

### Scenario 2: Debugging Tool Failure

**Goal:** Understand why tool fails in agent context

**Method:** API test → Direct invocation

1. Reproduce with API test, save tool call params from JSON
2. Test directly in Python with same params
3. Add debug prints, fix issue
4. Re-run API test to verify fix

**Alternative:** Use Studio for interactive debugging if API parsing is difficult

### Scenario 3: Verifying Agent Behavior

**Goal:** Confirm agent uses tools correctly

**Method:** Dev server + API test

1. Start dev server
2. Create test script with multiple queries
3. Parse streaming responses to extract tool calls
4. Verify agent called expected tools with correct params
5. Verify agent follows system prompt instructions

**Example:** Test that agent automatically calls cite_videos after mentioning videos

## What to Verify

**For tools:**
- ✓ Returns expected data structure
- ✓ Handles missing/invalid input
- ✓ External service connectivity (Supabase, APIs)
- ✓ Error messages are clear

**For agent:**
- ✓ Calls tools with correct parameters
- ✓ Follows system prompt instructions
- ✓ Handles tool errors gracefully
- ✓ Provides coherent responses

## Quick Reference

| Scenario | Method | Command |
|----------|--------|---------|
| Smoke test new tool | Direct | `python` → `from src.tools import X` |
| Test agent flow | Dev server + API | `langgraph dev` + test script |
| Debug tool failure | API + Direct | Test script → `python` debug |
| Verify integration | Dev server + API | `langgraph dev` + HTTP requests |
| Manual exploration | Studio (optional) | `langgraph dev` → browser |

## Common Mistakes

**Testing only via direct invocation**
- **Problem:** Misses agent integration issues
- **Fix:** Also test via dev server to verify real behavior

**Not starting dev server**
- **Problem:** Can't test streaming, agent flow, or integration
- **Fix:** Run `langgraph dev` for integration/end-to-end tests

**Creating many test files without running them**
- **Problem:** Unclear which to use, maintenance burden, tests not actually run
- **Fix:** Create 1-2 focused test scripts and actually run them. Commit working ones for regression testing.

**Skipping error cases**
- **Problem:** Tools break in production on bad input
- **Fix:** Test with missing params, invalid IDs, network failures

## Red Flags

**"Tool works in Python, testing complete"** → No. Start dev server, create API test, verify agent integration.

**Creating multiple test scripts but not running them** → Tests that don't run are documentation, not verification.

**"I've verified the function returns correct data"** → Good first step. Now create automated API test to verify agent integration.

**Using Studio exclusively** → Studio testing is manual and not repeatable. Write automated API tests instead.

**All of these mean: Create automated API test. Integration testing is not optional for new tools.**

## Integration

**Pairs with:**
- **test-driven-development** - Write tests before implementing tools
- **systematic-debugging** - Use when debugging tool/agent issues
