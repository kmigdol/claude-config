# Frontend Testing Conventions

## Stack

- **vitest** — Test runner
- **@testing-library/react** — Component testing
- **jsdom** — DOM environment

## Commands

```bash
pnpm test -- --run                    # Run all tests once (CI mode)
pnpm test -- --run path/to/test.tsx   # Run specific test file
pnpm test                             # Watch mode
```

## Patterns

### Zustand Store Tests
```tsx
beforeEach(() => {
  useCitationsStore.getState().clearAll();  // Reset store
  vi.clearAllMocks();
});
```

### scrollIntoView
`Element.prototype.scrollIntoView` is mocked globally (via setup file). Assert with:
```tsx
expect(Element.prototype.scrollIntoView).toHaveBeenCalledWith({
  behavior: 'smooth',
  block: 'start',
});
```

### Store Updates in Tests
Wrap store mutations in `act()`:
```tsx
act(() => {
  useCitationsStore.getState().addCitations('msg-1', [createMockCitation('123')]);
});
```

### Motion/Framer Mocks
```tsx
vi.mock('motion/react', () => ({
  LazyMotion: ({ children }) => <>{children}</>,
  MotionConfig: ({ children }) => <>{children}</>,
  domAnimation: {},
}));

vi.mock('motion/react-m', () => {
  const Div = ({ children, ...props }) => <div {...props}>{children}</div>;
  return { div: Div };
});
```

## File Locations

Tests live alongside their source files:
- `components/assistant-ui/citations-sidebar.tsx` → `citations-sidebar.test.tsx`
- `lib/citations-store.ts` → (tested through sidebar tests)
- `app/api/*/route.ts` → `route.test.ts`
