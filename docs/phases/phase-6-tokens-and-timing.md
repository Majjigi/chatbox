# Phase 6 — Token count and time taken under each answer

**Goal:** under every answer, show how many tokens it used and how long it took, so you can
compare models.

```
Claude · claude-opus-5-5 · 48 in / 264 out tokens · 2.41 s (first word after 620 ms)
```

## What was built

| File | What changed |
| ---- | ------------ |
| `models/chat.model.ts` | New `ReplyStats` type; `ChatMessage` gained `stats` |
| `services/chat-store.service.ts` | Saves the numbers from the `done` event onto the reply |
| `pipes/duration.pipe.ts` | New pipe: `850` → `"850 ms"`, `2410` → `"2.41 s"` |
| `components/message-bubble/` | Shows the stats line under finished replies |
| `app.component.scss`, `chat-header.component.scss` | Layout fixes so everything fits on phone screens |

The backend side was already done in phase 2 — the `done` event has carried these numbers
since then. This phase is about showing them.

## Key ideas

### 1. What tokens are

Models don't read letters or whole words; they read **tokens** — common chunks of text.
`"streaming"` might be one token, `"unbelievable"` might be three (`un` `believ` `able`).
Roughly, 1 token ≈ ¾ of an English word.

Tokens matter because they're what you **pay for** and what the model's **limits** are
measured in.

| Number | What it counts | Where it comes from |
| ------ | -------------- | ------------------- |
| **in** (input tokens) | Everything the model read: system prompt + the whole conversation + your new question | Gemini: `usage_metadata.prompt_token_count` · Claude: `usage.input_tokens` |
| **out** (output tokens) | Everything the model wrote, including hidden "thinking" | Gemini: `candidates_token_count + thoughts_token_count` · Claude: `usage.output_tokens` |

Notice that **input tokens grow with every turn**: each request re-sends the whole
conversation, so the 10th question costs more to ask than the 1st. That's why long chats get
more expensive.

The demo model can't count real tokens, so it counts words instead.

### 2. Two timings

| Number | Meaning | Why it matters |
| ------ | ------- | -------------- |
| **total** (`2.41 s`) | Request arrived → reply finished | How long the whole answer took |
| **first word** (`620 ms`) | Request arrived → first piece of text | How long the user stared at the "…" dots. Streaming makes an app *feel* fast even when the total is long |

Both are measured on the **backend** with `time.perf_counter()` (see `stream_reply_events()` in
`backend/app/api/routes/chat.py`), so they measure the model, not your network.

### 3. Getting numbers from the stream to the screen

```
backend:  data: {"type": "done", "input_tokens": 48, "output_tokens": 264, "total_ms": 2410, "first_token_ms": 620}
            │
store:    handleEvent(done) → reply.stats = { inputTokens: 48, outputTokens: 264, totalMs: 2410, firstTokenMs: 620 }
            │
bubble:   {{ stats.inputTokens | number }} in / {{ stats.outputTokens | number }} out tokens · {{ stats.totalMs | duration }}
```

The store converts the backend's `snake_case` names to the `camelCase` style TypeScript code
normally uses.

### 4. Pipes

A **pipe** formats a value inside a template: `{{ value | pipeName }}`.

- `number` is built into Angular: `1234` → `"1,234"`.
- `duration` is ours (`pipes/duration.pipe.ts`): `850` → `"850 ms"`, `2410` → `"2.41 s"`.

A component lists the pipes it uses in its `imports`.

## Try it

Ask the same question to each model and compare the line under the answers. Then ask a few
follow-ups and watch the **in** number climb as the conversation grows.

## Next

[Phase 7](phase-7-polish-and-docs.md) polishes the docs and explains how to record the demo
video.
