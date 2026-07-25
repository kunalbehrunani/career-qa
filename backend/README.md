# backend

NestJS service that receives a career question (plus an optional target company/domain), runs the local Python retrieval engine, and assembles a ready-to-use prompt — no LLM API call, no API key. You copy the result and paste it into ChatGPT, Claude, or any LLM chat yourself.

## Run

```bash
npm install
npm run start:dev
```

Runs on `http://localhost:3000`. Requires the Python retrieval engine to be set up first — see the [main README](../README.md#getting-started).

## API

**`POST /prompt`**

Request:
```json
{
  "question": "Tell me about your best project",
  "companyName": "Visa",
  "companyAbout": "Global payments company"
}
```
`companyName` and `companyAbout` are optional.

Response:
```json
{
  "prompt": "...the full assembled prompt, ready to paste...",
  "sources": [{ "source": "projects/payments.md", "section": "Outcome & Impact" }]
}
```

## Structure

```
src/
├── main.ts                          # bootstrap, CORS, validation pipe
├── app.module.ts
└── prompt/
    ├── prompt.controller.ts         # POST /prompt
    ├── prompt.service.ts            # assembles the final prompt text
    ├── retrieval.service.ts         # spawns retrieve.py, parses its JSON output
    └── dto/create-prompt.dto.ts
```
