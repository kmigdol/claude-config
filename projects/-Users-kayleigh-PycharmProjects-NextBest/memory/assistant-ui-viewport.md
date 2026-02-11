# assistant-ui Viewport & turnAnchor Behavior

## The Problem (NEX-129)

Setting `turnAnchor="top"` on `ThreadPrimitive.Viewport` causes a massive gap during streaming.

## Root Cause

The `@assistant-ui/react` library has an internal component called `ThreadPrimitiveViewportSlack` (in `node_modules/@assistant-ui/react/dist/primitives/thread/ThreadViewportSlack.js`).

When `turnAnchor="top"` is set:
- `MessagePrimitive.Root` wraps every message with `ViewportSlack`
- ViewportSlack applies **inline** `min-height: <viewport-height>px` and `flex-shrink: 0` to the **last assistant message** (when `message.isLast && message.index >= 2`)
- This ensures enough scroll room to anchor the top of the turn at the top of the viewport
- But during streaming, when the message content is short, this creates a huge visible gap

The min-height calculation: `Math.max(0, viewport - inset - clampAdjustment)`

## The Fix

Conditionally disable `turnAnchor` during streaming:

```tsx
const ThreadViewport: FC = () => {
  const isRunning = useAssistantState(({ thread }) => thread.isRunning);
  return (
    <ThreadPrimitive.Viewport
      turnAnchor={isRunning ? undefined : "top"}
    >
      {children}
    </ThreadPrimitive.Viewport>
  );
};
```

- `turnAnchor="top"` when idle → anchoring works for loading past conversations (NEX-127)
- `turnAnchor={undefined}` when streaming → no ViewportSlack min-height → no gap

## Key Insight

`useAssistantState` must be called **inside** `ThreadPrimitive.Root` context, not in the component that renders Root. Extract a child component if needed.

## Related: Composer Placement

Also moved Composer + FeedbackButton outside `ThreadPrimitive.Viewport` (but still inside `ThreadPrimitive.Root`). This keeps the composer fixed at the bottom without needing a `grow` spacer inside the scroll area.

Note: The Composer's `sticky bottom-0` only works when content overflows (scrolling occurs). Without enough content, sticky has no effect — moving it outside the viewport is the proper fix.

## Files

- `socialgpt-frontend/components/assistant-ui/thread.tsx` - ThreadViewport component with conditional turnAnchor
- `node_modules/@assistant-ui/react/dist/primitives/thread/ThreadViewportSlack.js` - Library source for ViewportSlack
- `node_modules/@assistant-ui/react/dist/primitives/message/MessageRoot.js` - Where ViewportSlack wraps messages
