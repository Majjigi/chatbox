# Phase 7 — Polish and full documentation

**Goal:** make the project easy for someone else to understand, run and extend.

## What was built

| File | What it does |
| ---- | ------------ |
| `README.md` | Overview, screenshot, quick start, project map, API, troubleshooting |
| `docs/how-it-works.md` | One question followed from Enter key to finished answer, with diagrams |
| `docs/images/chatbox.png` | The screenshot in the README |
| `backend/README.md`, `frontend/README.md` | Setup and structure for each half |

## How the documentation is organised

| If you want to… | Read |
| --------------- | ---- |
| Run the app | [README → Quick start](../../README.md#quick-start) |
| Understand the whole flow | [how-it-works.md](../how-it-works.md) |
| Learn one idea at a time | The phase pages, in order ([phase 1](phase-1-backend-foundation.md) → 6) |
| Work on only one half | [backend/README.md](../../backend/README.md) or [frontend/README.md](../../frontend/README.md) |
| Add a model | [README → Adding another model](../../README.md#adding-another-model-eg-openai) |

## Diagrams

The diagrams in `README.md` and `how-it-works.md` are written in
[Mermaid](https://mermaid.js.org/) — plain text inside a ` ```mermaid ` block. GitHub draws them
as pictures automatically, and they're easy to edit because they're just text.

## Recording the demo video

The task asks for a 30-second screen recording for your own use. Steps and a suggested script
are in [README → Recording a 30-second demo](../../README.md#recording-a-30-second-demo).
Recordings go in `recordings/`, which `.gitignore` keeps out of the repo.

## Checklist: is everything working?

- [ ] `cd backend && pytest` — all tests pass
- [ ] `cd frontend && npm test` — all tests pass
- [ ] http://localhost:8000/api/models lists your models with `"available": true`
- [ ] In the app, a reply streams in word by word
- [ ] The dropdown switches models; each reply is labelled with its model
- [ ] The system prompt changes the answers
- [ ] Token counts and time appear under each finished answer
- [ ] Stop cuts a reply off, and the label under it says "Stopped"

## Next

[Phase 8](phase-8-groq-instead-of-gemini.md) swaps Gemini for Groq, which has a free API key.
