# Phase 2 — Streaming endpoint with an offline demo model

**Goal:** an endpoint that sends a reply *while it's being written*, piece by piece, the way
ChatGPT does — proven end to end with a pretend model that needs no API key.

## What was built

| File | What it does |
| ---- | ------------ |
| `backend/app/schemas/chat.py` | The shapes of requests, responses and stream events |
| `backend/app/providers/base.py` | `ChatProvider`: the one method every model must offer |
| `backend/app/providers/demo_provider.py` | A pretend model that streams a canned reply word by word |
| `backend/app/providers/registry.py` | The list of models, and how to get the provider for one |
| `backend/app/api/routes/models.py` | `GET /api/models` — choices for the dropdown |
| `backend/app/api/routes/chat.py` | `POST /api/chat/stream` — runs a model and streams its reply |
| `backend/tests/test_chat_stream.py` | Tests for the stream, validation and error handling |

## Key ideas

### 1. Streaming with Server-Sent Events (SSE)

Language models write one token (a word or piece of a word) at a time. Waiting for the
whole answer would leave the user staring at a blank screen for seconds, so we forward each
piece as soon as it exists.

`StreamingResponse` sends whatever our generator `yield`s immediately. We format each piece
as an SSE event — `data: ` + JSON + a blank line:

```
data: {"type": "token", "text": "Hi! "}

data: {"type": "token", "text": "I'm "}

data: {"type": "done", "input_tokens": 3, "output_tokens": 64, "total_ms": 3111, "first_token_ms": 42}
```

There are three event types (see `schemas/chat.py`):

| `type` | Meaning | Extra fields |
| ------ | ------- | ------------ |
| `token` | The next piece of the reply | `text` |
| `done` | The reply finished | `input_tokens`, `output_tokens`, `total_ms`, `first_token_ms` |
| `error` | Something failed mid-reply | `message` |

**Why errors are events:** the HTTP status code (`200 OK`) goes out with the very first
event. If the model fails halfway, it's too late to send `500`, so the failure travels as an
`error` event instead. Errors found *before* streaming starts (unknown model, missing API
key) are still normal HTTP errors (`404`, `400`).

### 2. Async generators

```python
async def stream_reply(self, messages, system_prompt):
    for word in words:
        await asyncio.sleep(WORD_DELAY_SECONDS)   # wait without blocking the server
        yield ChatChunk(text=word)                # hand out one piece
```

- `yield` turns a function into a **generator**: it hands out values one at a time instead
  of returning a whole list at the end.
- `async` + `await` let the server do other work (like serving another browser tab) while
  this function waits for the model.
- The caller reads it with `async for chunk in provider.stream_reply(...)`.

### 3. Providers: one interface, many models

The chat route never talks to Gemini or Claude directly. It asks the **registry** for a
**provider** and calls `stream_reply(...)`. Every provider follows the same template
(`ChatProvider` in `base.py`), so adding a model later means writing one new class — the
route doesn't change.

```
chat route ──► registry.get_provider("demo") ──► DemoProvider.stream_reply(...)
                                             └─► (phase 3) GeminiProvider / ClaudeProvider
```

### 4. Measuring time and tokens

`stream_reply_events()` in `chat.py` starts a stopwatch (`time.perf_counter()`) when the
request arrives and records:

- **first_token_ms** — when the first text arrived (how long the user waited for anything)
- **total_ms** — when the reply finished

Token counts come from the provider's last chunk (models only know the totals once they're
done). The demo model counts words as a stand-in for real tokens.

## Try it

Start the server (`uvicorn app.main:app --reload --reload-dir app`), then:

```bash
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"model": "demo", "messages": [{"role": "user", "content": "Hi!"}]}'
```

`-N` turns off curl's buffering, so you see the events arrive one by one. Or use the
Swagger page at http://localhost:8000/docs (it shows the result only once it's complete).

## Next

[Phase 3](phase-3-real-models.md) adds Gemini and Claude as providers (Gemini was later swapped for Groq in [phase 8](phase-8-groq-instead-of-gemini.md)).
