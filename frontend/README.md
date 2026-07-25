# frontend

Vue 3 + Vite + Tailwind CSS. A form for company name, company context, and your question — calls the backend and shows a copy-ready prompt with a Reset and Copy button.

## Run

```bash
npm install
npm run dev
```

Runs on `http://localhost:5173`. The [backend](../backend/README.md) must be running at the same time (`http://localhost:3000`) — the form calls it directly.

## Structure

```
src/
├── App.vue                    # the form + generated-prompt panel
├── services/promptApi.ts      # POST /prompt call to the backend
└── style.css                  # Tailwind import
```
