# Phase 4 — Angular chat screen

**Goal:** a chat screen in the browser — message bubbles and a text box — that shows the
reply appearing word by word as the backend streams it.

## What was built

| File | What it does |
| ---- | ------------ |
| `frontend/src/app/app.component.*` | The page layout: header, messages, text box |
| `components/chat-header/` | App name, the model being used, "New chat" button |
| `components/message-list/` | The scrolling list (auto-scrolls as text arrives) and a welcome screen |
| `components/message-bubble/` | One bubble; shows a typing indicator, a blinking cursor, errors |
| `components/chat-input/` | The text box; Enter sends, Shift+Enter adds a line; Send turns into Stop |
| `services/chat-api.service.ts` | Calls the backend and reads the streamed reply |
| `services/chat-store.service.ts` | Holds the chat state and the actions `send`, `stop`, `clearChat` |
| `models/chat.model.ts` | TypeScript types matching the backend's data |
| `utils/sse-parser.ts` | Turns the raw streamed text into event objects |
| `*.spec.ts` | Tests for the parser and the store |

## How a message travels

```
You press Enter
  └─► ChatInputComponent.send()
        └─► ChatStoreService.send("Hi")
              ├─ adds your bubble + an empty reply bubble (status: "streaming")
              └─► ChatApiService.streamChat(request)
                    └─ fetch POST /api/chat/stream ──► FastAPI
                         ◄── data: {"type":"token","text":"Hel"}
                    SseParser turns text into events
              ◄── handleEvent(token) → reply.content += "Hel"
                    (the signal changes → the bubble re-renders)
              ◄── handleEvent(done)  → reply.status = "done"
```

## Key ideas

### 1. Components and services

- **Components** draw a part of the screen. Each has a `.ts` (logic), `.html` (template) and
  `.scss` (styles) file.
- **Services** hold logic shared between components. There are two:
  - `ChatApiService` only talks to the backend.
  - `ChatStoreService` holds the state and decides what happens when you send or stop.

Components get a service with `inject(ChatStoreService)` — Angular hands every component the
same instance, so they all see the same messages.

### 2. Signals

The store keeps its state in **signals**:

```ts
readonly messages = signal<ChatMessage[]>([]);   // create
this.messages();                                  // read (it's a function call)
this.messages.update((list) => [...list, msg]);   // change
```

When a signal changes, Angular re-draws exactly the parts of the screen that read it. That's
how each new token appears in the bubble without any extra code: the store appends the text,
and the bubble updates.

`computed(...)` creates a signal worked out from others (e.g. `canSend` in the text box is true
only when there's text, a model, and no reply in progress).

### 3. Reading a stream with `fetch`

Angular's `HttpClient` gives you the response only once it has fully arrived — useless for
streaming. So `streamChat()` uses the browser's own `fetch()` and reads the body piece by piece:

```ts
const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
while (true) {
  const { value, done } = await reader.read();   // waits for the next piece of text
  if (done) return;
  for (const event of parser.push(value)) onEvent(event);
}
```

Pieces don't line up with events — one piece can hold half an event or several. `SseParser`
keeps leftover text until the blank line that ends each event arrives.

### 4. Stopping a reply

`streamChat()` returns an RxJS `Observable`. When the store unsubscribes (Stop button), the
`AbortController` cancels the `fetch`. The backend notices the browser went away and stops
asking the model for more text, so you don't pay for tokens nobody will read.

### 5. Sending the history

Each request contains the earlier conversation (see `toHistory()` in the store), because the
model has no memory of its own. Only complete question + answer pairs are sent, so a reply
that failed before writing anything doesn't leave a dangling question.

## Try it

Terminal 1 — backend:

```bash
cd backend
uvicorn app.main:app --reload --reload-dir app
```

Terminal 2 — frontend:

```bash
cd frontend
npm install
npm start
```

Open http://localhost:4200, type a message and press Enter. Without API keys the
**Demo model** answers. Press **Stop** while it's writing to cut the reply off.

Run the frontend tests with `npm test`.

## Next

[Phase 5](phase-5-model-dropdown-system-prompt.md) adds the model dropdown and the system
prompt box.
