# ChatBox — Frontend

The chat screen, built with [Angular](https://angular.dev/) 22 (standalone components, signals,
SCSS, Vitest).

## Project structure

```
frontend/src/
├── app/
│   ├── app.component.*            # The page layout: header, messages, text box
│   ├── app.config.ts              # App-wide providers (HttpClient)
│   ├── components/
│   │   ├── chat-header/           # App name, model in use, "New chat"
│   │   ├── message-list/          # Scrolling list of messages + empty screen
│   │   ├── message-bubble/        # One message bubble
│   │   └── chat-input/            # Text box + Send / Stop
│   ├── services/
│   │   ├── chat-api.service.ts    # Talks to the backend (incl. reading the stream)
│   │   └── chat-store.service.ts  # Chat state (signals) + actions: send, stop, clear
│   ├── models/
│   │   └── chat.model.ts          # TypeScript types for messages and API data
│   └── utils/
│       └── sse-parser.ts          # Splits the streamed text into events
├── environments/                  # Backend URL for development / production
└── styles.scss                    # Colour tokens (light + dark) and shared buttons
```

Every component has its own folder with separate `.ts`, `.html` and `.scss` files.

## Setup

Requires [Node.js](https://nodejs.org/) 22 or newer.

```bash
cd frontend
npm install
```

## Run

Start the [backend](../backend/README.md) first, then:

```bash
npm start
```

Open http://localhost:4200. The app expects the API at `http://localhost:8000/api`
(set in `src/environments/environment.development.ts`).

## Test

```bash
npm test
```

## Generate new code

The Angular CLI is set up to create files with the same naming as the rest of the project:

```bash
npx ng generate component components/my-thing   # → my-thing.component.ts/.html/.scss
npx ng generate service services/my-thing        # → my-thing.service.ts
```
