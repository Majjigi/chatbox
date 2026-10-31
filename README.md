# ChatBox

A small ChatGPT-style app built to learn how AI chat apps work end to end:

- **Angular** chat screen with message bubbles and a text box
- **FastAPI** (Python) backend that **streams** the model's reply token by token
- A **dropdown** to switch between models (Gemini and Claude)
- A **system prompt** box to steer the model
- **Token count** and **time taken** under every answer

It runs locally only — nothing is deployed.

## Build phases

The project is built in small steps. Each phase is one git commit with a tag
(`phase-1`, `phase-2`, …), so you can check out any step and see the code at that point:

```bash
git checkout phase-1   # see the code as it was after phase 1
git checkout main      # back to the finished app
```

| Phase | What gets built | Status |
| ----- | --------------- | ------ |
| [1](docs/phases/phase-1-backend-foundation.md) | Backend foundation: FastAPI app, settings, CORS, health check | ✅ |
| [2](docs/phases/phase-2-streaming-demo-model.md) | Streaming endpoint with an offline demo model | ✅ |
| [3](docs/phases/phase-3-real-models.md) | Real AI models: Gemini and Claude | ✅ |
| [4](docs/phases/phase-4-angular-chat-screen.md) | Angular chat screen: bubbles, text box, live streaming | ✅ |
| [5](docs/phases/phase-5-model-dropdown-system-prompt.md) | Model dropdown and system prompt box | ✅ |
| 6 | Token count and time taken under each answer | ⏳ |
| 7 | Polish and full documentation | ⏳ |

## Run it

1. Backend: see [backend/README.md](backend/README.md)
2. Frontend: see [frontend/README.md](frontend/README.md)
