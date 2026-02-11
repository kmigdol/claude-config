# Citations Data Flow

## End-to-End Flow

```
Streaming AI message (assistant.tsx)
  → extractTikTokIdsFromText(textContent)
  → fetchCitations(videoIds, messageId)
  → useCitationsStore.getState().addCitations(messageId, citations)
  → CitationsSidebar re-renders (watches citations.length)
  → Auto-scroll to first new citation (if new message_id)
```

## Key Files

- `app/assistant.tsx` (lines ~249-292) — Extracts TikTok IDs during streaming, fetches citation data, adds to store
- `lib/citations-store.ts` — Zustand store, deduplicates by `tiktok_id`, appends with `message_id`
- `lib/types/citations.ts` — `TikTokCitation` interface (includes `message_id`, `expanded`)
- `components/assistant-ui/citations-sidebar.tsx` — Renders citations, auto-scrolls
- `components/assistant-ui/citation-card.tsx` — Individual citation card UI

## Store Shape

```ts
interface CitationsStore {
  citations: TikTokCitation[];
  addCitations: (messageId: string, citations: Omit<TikTokCitation, 'message_id'>[]) => void;
  toggleExpanded: (tiktokId: string) => void;
  clearAll: () => void;
}
```

## Auto-Scroll Logic (NEX-128)

- Tracks `prevCountRef` (previous citation count) and `scrolledMessageRef` (last scrolled message_id)
- Only scrolls for the **first citation of a new message** — subsequent citations from the same message don't trigger scroll
- Uses `scrollIntoView({ behavior: 'smooth', block: 'start' })`
- Ref attached to citation at index `prevCountRef.current` (first new one)

## Citation Extraction Timing

Citations are extracted progressively during streaming:
- `messages/partial` events trigger extraction as text streams in
- `messages/complete` events trigger final extraction
- Store deduplication prevents duplicates from repeated processing
- Tool call results are also tracked via `toolCallToAiMessageMap`
