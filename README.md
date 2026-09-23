# Google Sheets Two-Way Sync

A small, production-minded monorepo demonstrating near-real-time synchronization between a React table and a Google Sheet. The Sheet is the source of truth: FastAPI reads and updates it, a polling worker detects external edits, and Socket.IO pushes changed data to connected browsers.

## Features

- React/Vite single-page UI with a table containing exactly `A`, `B`, and `C`
- Row picker and modal editor outside the table; no Actions column is added
- Exact physical row mapping (`row: 3` updates `A3:C3`)
- Google service-account authentication only on the backend
- Optimistic concurrency: an outdated client hash gets `409 Conflict`, then reloads
- Near-real-time Google Sheet to browser sync using a two-second poll and Socket.IO
- Protected internal broadcast endpoint and origin-restricted CORS
- FastAPI OpenAPI documentation at `/docs`, automated unit tests, and Docker support

## Architecture

```text
React + Vite  -- REST -->  FastAPI  -- Google Sheets API --> Google Sheet
     ^                         |
     | Socket.IO               | poll A:C every 2 seconds / changed hash
     +------ Node/Express <----+
```

The Python service reads `Sheet1!A:C`, normalizes every row to three values (including empty cells), hashes the canonical `row/A/B/C` representation, and broadcasts only when that hash changes. Google Sheets has no simple browser-facing row-change webhook for this use case, so this is **near-real-time** rather than true real-time: external changes usually appear within 0-2 seconds plus Google API and network latency.

## Layout

```text
backend/           FastAPI, Sheets client, polling worker, tests
frontend/          React UI, REST/socket clients, components
realtime-service/  Express + Socket.IO protected broadcaster
docker-compose.yml Optional three-service local container setup
```

## Google Cloud setup

1. Create a Google Cloud project and enable the **Google Sheets API**.
2. Create a service account and generate a JSON key.
3. Share the target Sheet with the service account's `client_email` as Editor.
4. Ensure row 1 is headers `A | B | C`; put demonstration data in rows 2-5.
5. Copy each `.env.example` to `.env` locally (these files are ignored) and map the key values to the backend variables. For `GOOGLE_PRIVATE_KEY`, preserve newlines as `\n` if entered on one line.

Required backend values are `GOOGLE_PROJECT_ID`, `GOOGLE_CLIENT_EMAIL`, `GOOGLE_PRIVATE_KEY`, and `GOOGLE_SHEET_ID`. `GOOGLE_SHEET_RANGE` defaults to `Sheet1!A:C`. Set the same long random value for `BACKEND_API_KEY` in the backend and realtime service. `FRONTEND_ORIGINS` and `FRONTEND_URL` must contain the actual frontend origin in production.

## Run locally

Use three terminals after creating local `.env` files from the examples.

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

```powershell
cd realtime-service
npm install
npm run dev
```

```powershell
cd frontend
npm install
npm run dev
```

The backend is at `http://localhost:8000`, Swagger is at `http://localhost:8000/docs`, Socket.IO is at `http://localhost:3001`, and Vite normally serves the UI at `http://localhost:5173`.

## API

`GET /` returns the service message; `GET /health` returns health; `GET /api/sheet` returns `{ data, hash }`; and `PUT /api/sheet/{row}` accepts `A`, `B`, `C`, and optional `expected_hash`. Row 1 is rejected, missing rows return 404, and a stale hash returns 409 rather than overwriting an external edit.

## Testing

```powershell
cd backend; python -m pytest
cd frontend; npm test
cd realtime-service; npm test
```

Backend tests cover normalization, empty cells, row mapping, and deterministic hashing. The frontend test verifies the three-column table contract. Manually verify: website-to-Sheet edit, direct Sheet-to-website edit, multiple edits, empty C, invalid row, and a conflict after an external edit.

## Deployment

Deploy the frontend and both long-running services separately. As checked on September 22, 2026, [Vercel Hobby](https://vercel.com/docs/plans/hobby) is free for personal/non-commercial frontend projects, while [Render](https://render.com/pricing) advertises free compute suitable for prototypes. Free plans can sleep, change, or impose usage limits; check the current terms before submitting. Use a paid/always-on service if dependable two-second polling is required.

Set the frontend's `VITE_API_URL` and `VITE_SOCKET_URL` to public HTTPS URLs, backend `FRONTEND_ORIGINS` to the frontend URL, and realtime `FRONTEND_URL` to the same frontend URL. Never deploy `localhost` values or credentials to the browser.

## Security and limitations

Secrets are ignored and never shipped to the frontend. The Node broadcast route requires `X-Backend-Key`; CORS is allowlisted instead of wildcarded. This implementation intentionally has no database, authentication, or distributed queue. It is limited by polling latency, Sheets API quotas, free-host restarts/sleeping, and process-local polling state. For multi-instance production, add a leader/lock and shared pub/sub; future work could add Google Workspace event integration, retries/backoff, audit logs, authentication, and more granular updates.
