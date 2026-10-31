# Phase 3 — Real AI models: Gemini and Claude

**Goal:** plug two real language models into the streaming endpoint from phase 2, so the same
`POST /api/chat/stream` can be answered by Google's Gemini or Anthropic's Claude.

## What was built

| File | What it does |
| ---- | ------------ |
| `backend/app/providers/gemini_provider.py` | Streams a reply from Gemini with the `google-genai` SDK |
| `backend/app/providers/claude_provider.py` | Streams a reply from Claude with the `anthropic` SDK |
| `backend/app/providers/registry.py` | Now lists Gemini and Claude too, greyed out if their key is missing |
| `backend/app/core/config.py` | New settings: `GEMINI_API_KEY`, `GEMINI_MODEL`, `ANTHROPIC_API_KEY`, `CLAUDE_MODEL` |
| `backend/tests/test_providers.py` | Checks each provider builds the right request (no real API calls) |

## Key ideas

### 1. Same interface, different SDKs

Both new classes follow the `ChatProvider` template from phase 2, so the chat route didn't
change at all. Each one hides its SDK's quirks:

| | Gemini | Claude |
| --- | --- | --- |
| SDK call | `client.aio.models.generate_content_stream(...)` | `client.beta.messages.stream(...)` |
| Name for the assistant's role | `"model"` (we convert `"assistant"`) | `"assistant"` (same as ours) |
| System prompt goes in | `config.system_instruction` | `system` |
| Token counts come from | `usage_metadata` on each chunk (last one is final) | `usage` on the final message |

### 2. Sending the whole conversation every time

Models don't remember anything between requests. To ask a follow-up question, the browser
sends the **entire conversation so far**, and the provider passes it all to the model. That's
also why you can switch models mid-conversation: the new model simply reads the history the
old one wrote.

### 3. API keys stay on the server

The browser never sees an API key. It calls *our* backend, and only the backend talks to Google
and Anthropic, using keys from `backend/.env` (which git ignores). If a key is missing, the
model still appears in `GET /api/models` with `"available": false`, so the dropdown can show it
greyed out instead of failing later.

### 4. Friendly errors

Each provider catches its SDK's errors and turns them into a `ProviderError` with a sentence the
user can act on, for example:

- `Claude rejected the API key. Check ANTHROPIC_API_KEY in backend/.env.`
- `Gemini's rate limit or free quota was reached. Wait a minute and try again.`

The chat route sends that sentence to the browser as an `error` event.

### 5. Claude settings worth knowing

- `max_tokens: 64000` — an upper limit, not a target. You pay only for what's written.
- `output_config: {"effort": "low"}` — Claude thinks briefly before answering; low effort keeps
  chat replies quick. Raise it (`"medium"`, `"high"`) for harder questions.
- `fallbacks: "default"` — on the newest Claude models, if a safety filter declines a request,
  Anthropic retries it on a suitable other model automatically. It's a beta feature, which is
  why the code uses `client.beta.messages`.

## Try it

1. Get an API key: Gemini at https://aistudio.google.com/apikey, Claude at
   https://platform.claude.com
2. Put it in `backend/.env`:
   ```
   GEMINI_API_KEY=your-key-here
   ANTHROPIC_API_KEY=your-key-here
   ```
3. Restart the server, open http://localhost:8000/api/models — your model now shows
   `"available": true`.
4. Stream a reply (use the `id` from `/api/models` as `model`):
   ```bash
   curl -N -X POST http://localhost:8000/api/chat/stream \
     -H "Content-Type: application/json" \
     -d '{"model": "gemini-flash-latest", "messages": [{"role": "user", "content": "Write a haiku about rain"}]}'
   ```

## Next

[Phase 4](phase-4-angular-chat-screen.md) builds the Angular chat screen.
