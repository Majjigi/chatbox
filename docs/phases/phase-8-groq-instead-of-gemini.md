# Phase 8 — Swap Gemini for Groq (free API key)

**Goal:** replace Google's Gemini with [Groq](https://groq.com/), whose API has a free plan,
so the app can talk to a real model without paying anything.

Groq doesn't make its own models. It *hosts* open models — such as OpenAI's open-weight
`gpt-oss` and Meta's Llama — on custom chips that write text very fast.

## What changed

| File | What changed |
| ---- | ------------ |
| `backend/app/providers/groq_provider.py` | **New:** streams replies from Groq with the `groq` SDK |
| `backend/app/providers/gemini_provider.py` | **Removed** |
| `backend/app/providers/registry.py` | The dropdown entry is now `Groq · openai/gpt-oss-120b` |
| `backend/app/core/config.py` | `GROQ_API_KEY` and `GROQ_MODEL` replace the Gemini settings; unknown lines in `.env` are now ignored instead of crashing |
| `backend/requirements.txt` | `groq` replaces `google-genai` |
| `backend/tests/test_providers.py` | Tests for how the Groq request is built |
| `frontend/src/app/models/chat.model.ts` | The `provider` type lists `'groq'` instead of `'gemini'` |

The chat route, the streaming format and the whole Angular UI did **not** change. That's the
payoff of the provider pattern from phase 2: swapping a model means writing one new class and
updating the list of models.

## Key ideas

### 1. The "chat completions" format

Groq uses the same request format as OpenAI's API, which many providers copy. The system
prompt isn't a separate field — it's just the first message, with the role `system`:

```python
messages = [
    {"role": "system", "content": "You are a pirate."},     # only if a system prompt was set
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Ahoy!"},
    {"role": "user", "content": "Where's the treasure?"},
]
```

See `build_request()` in `groq_provider.py`.

### 2. Reading the stream

With `stream=True`, the SDK hands back chunks. Each one holds the next bit of text in
`chunk.choices[0].delta.content`:

```python
stream = await self.client.chat.completions.create(model=..., messages=..., stream=True)
async for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        yield ChatChunk(text=chunk.choices[0].delta.content)
```

The **last** chunk carries the token counts. Groq puts them in its own `x_groq.usage` field
(newer API versions also fill the standard `usage` field), so the provider checks both.

### 3. Reasoning models

`gpt-oss` models *think* before they answer. Groq sends that thinking separately from the
answer (in `delta.reasoning`), and ChatBox simply doesn't display it. The thinking still
counts as **output tokens**, the same as with Claude.

`reasoning_effort: "low"` keeps the thinking short, so the first word appears sooner. Only
gpt-oss models accept that setting, so it's added only when the model id starts with
`openai/gpt-oss`.

### 4. Free-plan limits

Groq's free plan limits how much you can use per minute and per day — at the time of writing,
for `openai/gpt-oss-120b`, about 30 requests and 8,000 tokens per minute. Your real limits are
at https://console.groq.com/settings/limits. Two things follow from that:

- `max_completion_tokens` is set to 4,096. Groq counts the *requested* maximum reply length
  against your per-minute token allowance, so asking for a huge maximum can get even a short
  question rejected with `413 Request too large`.
- Long conversations re-send more tokens each turn, so they hit the limit sooner. Click
  **New chat** to start small again.

When a limit is hit, the error appears under the reply as a sentence, e.g.
"Groq's free rate limit was reached. Wait a minute and try again."

## Try it

1. Create a free key at https://console.groq.com/keys (no credit card needed).
2. Put it in `backend/.env`:
   ```
   GROQ_API_KEY=gsk_your-key-here
   ```
3. Restart the backend, then reload http://localhost:4200. **Groq · openai/gpt-oss-120b** is now
   selected in the dropdown.
4. Ask something and compare the time under the answer with Claude's — Groq is usually much
   faster.

Other models to try in `GROQ_MODEL`: `openai/gpt-oss-20b` (smaller, even faster) or
`llama-3.3-70b-versatile` (no thinking step, so the first word appears almost instantly). The
list is at https://console.groq.com/docs/models.
