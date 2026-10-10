# Portfolio RAG Agent Backend

Google ADK portfolio assistant using Gemini embeddings, semantic retrieval, a generated JSON vector index, and SSE APIs.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Set `GOOGLE_API_KEY` in `.env`.

## Test sequence

```bash
python scripts/ingest_knowledge.py --dry-run
pytest -q
python scripts/ingest_knowledge.py
python tests/evaluate_retrieval.py
```

The unit tests mock embeddings and do not consume API quota. Index generation and retrieval evaluation call the Gemini embedding API.

## Run the API locally

```bash
adk api_server --host 0.0.0.0 --port 8000 --allow_origins=http://localhost:5173 .
```

## Test the API

Create a session:

```bash
curl -X POST http://localhost:8000/apps/portfolio_agent/users/test-user/sessions/test-session -H "Content-Type: application/json" -d '{"source":"local-test"}'
```

Send an SSE request:

```bash
curl -N -X POST http://localhost:8000/run_sse -H "Content-Type: application/json" -H "Accept: text/event-stream" -d '{"appName":"portfolio_agent","userId":"test-user","sessionId":"test-session","newMessage":{"role":"user","parts":[{"text":"What experience does Kunal have with Google ADK?"}]},"streaming":true}'
```

## Docker

```bash
docker build -t portfolio-agent-backend .
docker run --rm -p 8000:8000 -e GOOGLE_API_KEY="your-key" -e ALLOWED_ORIGINS="http://localhost:5173" portfolio-agent-backend
```

## Deployed smoke test

```bash
python scripts/smoke_test_api.py --base-url https://your-backend.example.com
```

## Automatic index refresh

Add `GOOGLE_API_KEY` under GitHub repository Settings > Secrets and variables > Actions. The update workflow runs when the knowledge Markdown changes, weekly, or manually.

The generated JSON contains the original public chunks. Do not add confidential information to the knowledge folder.
