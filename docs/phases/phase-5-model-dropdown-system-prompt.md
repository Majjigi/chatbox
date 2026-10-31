# Phase 5 — Model dropdown and system prompt box

> **Update:** [Phase 8](phase-8-groq-instead-of-gemini.md) later replaced Gemini with Groq. This page describes the code as it was at the `phase-5` tag.

**Goal:** let the user choose which model answers, and steer it with a system prompt.

## What was built

| File | What changed |
| ---- | ------------ |
| `components/chat-header/` | The model badge became a `<select>` dropdown filled from `GET /api/models` |
| `components/system-prompt/` | New: a fold-out box with a textarea for the system prompt |
| `services/chat-store.service.ts` | New `systemPrompt` signal and `selectModel()`; each reply records `modelLabel` |
| `components/message-bubble/` | Shows which model wrote each reply |
| `models/chat.model.ts` | `ChatMessage` gained `modelLabel` |

## Key ideas

### 1. The dropdown is driven by the backend

The frontend doesn't hard-code any model names. On start-up the store calls
`GET /api/models` and the dropdown shows whatever comes back:

```json
[
  { "id": "gemini-flash-latest", "label": "Gemini · gemini-flash-latest", "provider": "gemini", "available": true },
  { "id": "claude-opus-5-5", "label": "Claude · claude-opus-5-5", "provider": "claude", "available": false },
  { "id": "demo", "label": "Demo model (offline)", "provider": "demo", "available": true }
]
```

- Models with `"available": false` (no API key) are shown but **disabled**, with "(no API key)".
- The first available model is **pre-selected**.
- Changing `GEMINI_MODEL` or `CLAUDE_MODEL` in `backend/.env` changes the dropdown — no frontend
  change needed.

The dropdown is disabled while a reply is streaming, so the model can't change mid-answer.

### 2. What a system prompt is

A system prompt is a set of instructions the model treats as standing rules for the whole
conversation — "You are a pirate", "Answer in French", "Reply in one sentence". It's sent with
**every** request (models remember nothing between requests) in a separate field from the
conversation:

```json
{
  "model": "claude-opus-5-5",
  "system_prompt": "You are a pirate. Answer in one sentence.",
  "messages": [{ "role": "user", "content": "What's your favourite treasure?" }]
}
```

Each provider puts it where its API expects it (Gemini: `system_instruction`, Claude: `system`).
Try the same question with different system prompts to see how much it changes the answer.

### 3. Switching models mid-conversation

Because the browser sends the whole history every time, you can ask Gemini a question, switch
to Claude, and ask a follow-up — Claude reads Gemini's earlier answer as part of the
conversation. Each reply is labelled with the model that wrote it so you can compare.

### 4. `<details>` for the fold-out box

The system prompt box uses the built-in HTML `<details>` / `<summary>` elements, which open and
close on click with no TypeScript at all. When closed, the summary shows a one-line preview of
the current prompt.

## Try it

1. Open the **System prompt** box and type `You are a pirate. Answer in one sentence.`
2. Ask "What's your favourite treasure?" — with the Demo model the reply repeats your system
   prompt back; with a real model it answers in pirate speak.
3. Switch the dropdown to another model and ask a follow-up.

## Next

[Phase 6](phase-6-tokens-and-timing.md) shows token counts and time taken under each answer.
