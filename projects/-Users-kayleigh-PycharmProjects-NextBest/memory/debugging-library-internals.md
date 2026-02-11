# Debugging Library Internals (@assistant-ui/react)

## When to Check Library Source

If a layout/behavior issue doesn't trace to our own code:
- Unexpected inline styles appearing on elements
- Flex/sizing behavior that doesn't match our CSS classes
- Components rendering differently than expected

## Where to Look

```
node_modules/@assistant-ui/react/dist/
├── primitives/
│   ├── thread/
│   │   ├── ThreadViewport.js          — Viewport component
│   │   ├── ThreadViewportSlack.js     — ViewportSlack (min-height for turnAnchor)
│   │   └── useThreadViewportAutoScroll.js — Auto-scroll logic
│   └── message/
│       └── MessageRoot.js             — Wraps messages with ViewportSlack
├── context/
│   ├── stores/ThreadViewport.js       — Viewport state store
│   └── providers/ThreadViewportProvider.js
```

## Key Internals

### ViewportSlack
- Applied by `MessagePrimitive.Root` to every message
- When `turnAnchor="top"` + message is last + index >= 2:
  - Sets inline `min-height: <viewport-height>px`
  - Sets inline `flex-shrink: 0`
- These are **inline styles** — can only be overridden with `!important` or structural changes
- Accepts `fillClampThreshold` and `fillClampOffset` props (passed through MessageRoot)

### Auto-scroll
- Default: scrolls to bottom as new content arrives
- `turnAnchor="top"`: anchors scroll at top of latest turn
- `scrollToBottomOnRunStart`: scrolls to bottom when assistant starts

## Lesson Learned

Don't assume our CSS classes are the only thing affecting layout. The library applies inline styles that override class-based styling. Always inspect the actual DOM if layout doesn't match expectations.
