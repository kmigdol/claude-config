# assistant-ui Mock Patterns for Testing

## Full Mock Setup (thread.test.tsx)

When testing components that use `@assistant-ui/react`, you need extensive mocks. Here's the working pattern:

```tsx
vi.mock('@assistant-ui/react', () => ({
  ThreadPrimitive: {
    Root: ({ children, ...props }: any) => <div data-testid="thread-root" {...props}>{children}</div>,
    Viewport: ({ children, ...props }: any) => {
      capturedViewportProps = props;  // Capture props for assertions
      return <div data-testid="thread-viewport" {...props}>{children}</div>;
    },
    Messages: () => <div data-testid="messages" />,
    If: ({ children }: any) => <>{children}</>,
    ScrollToBottom: ({ children }: any) => <>{children}</>,
    Suggestion: ({ children }: any) => <>{children}</>,
  },
  ComposerPrimitive: {
    Root: ({ children }: any) => <div>{children}</div>,
    Input: () => <input />,
    Send: ({ children }: any) => <>{children}</>,
    Cancel: ({ children }: any) => <>{children}</>,
    AttachmentDropzone: ({ children }: any) => <div>{children}</div>,
  },
  ActionBarPrimitive: {
    Root: ({ children }: any) => <div>{children}</div>,
    Copy: ({ children }: any) => <>{children}</>,
    Reload: ({ children }: any) => <>{children}</>,
    Edit: ({ children }: any) => <>{children}</>,
  },
  MessagePrimitive: {
    Root: ({ children }: any) => <div>{children}</div>,
    Parts: () => <div />,
    If: () => null,
    Error: ({ children }: any) => <>{children}</>,
  },
  ErrorPrimitive: {
    Root: ({ children }: any) => <div>{children}</div>,
    Message: () => <span />,
  },
  BranchPickerPrimitive: { Root: () => null },
  // useAssistantState must support selector pattern
  useAssistantState: (selector: (state: any) => any) => selector({
    thread: { isRunning: false, messages: [] },
    message: { isLast: false, index: 0 },
  }),
  useScrollLock: () => vi.fn(),
}));
```

## Key Gotchas

- `useAssistantState` takes a **selector function**, not just returns a value. The mock must call the selector with a mock state object.
- `ThreadPrimitive.If` should render children unconditionally in tests (pass-through).
- Motion libraries need separate mocks for `motion/react` and `motion/react-m`.
- Also mock: `@/lib/debug-mode`, `@/lib/supabase/client`, `next/navigation`, and all local component imports.
