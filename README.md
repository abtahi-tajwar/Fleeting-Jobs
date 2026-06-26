# Fleeting Jobs

A full-stack app that scrapes company career pages, parses listings with CSS selectors stored in PostgreSQL, filters jobs with AI, and extracts structured requirements from each listing.

## Architecture

| Layer | Stack | Port |
|-------|-------|------|
| Frontend | Next.js | 3000 |
| Backend API | Java Spring Boot | 8000 |
| Worker | Python (Playwright + OpenAI) | 8001 |
| Database | PostgreSQL (Docker) | 5432 |

Spring Boot owns the REST API, database, and scan orchestration. The Python **worker** handles headless browser scraping, HTML parsing, and LLM calls.

## Setup

### 1. PostgreSQL

```bash
docker compose up -d
```

### 2. Python worker

```bash
cd worker
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # set OPENAI_API_KEY
uvicorn main:app --reload --port 8001
```

### 3. Spring Boot backend

Requires Java 17+ and Maven.

```bash
cd backend
mvn spring-boot:run
```

API runs at [http://localhost:8000](http://localhost:8000).

On first startup, sample RBC company + parser data is seeded if the database is empty.

### 4. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## UI

- **Top bar:** Fleeting Jobs + Scan jobs
- **Sidebar:** Jobs, Companies, Parsers
- **Companies:** Add company name, listing URL, single post URL format
- **Parsers:** Select company, paste listing page JSON + company page JSON

## Worker endpoints (internal)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/scrape` | Headless browser HTML fetch |
| POST | `/parse/listing` | CSS parser for job links |
| POST | `/parse/job` | CSS parser for job description |
| POST | `/llm/filter-jobs` | Category matching |
| POST | `/llm/extract-details` | Extract skills, location, experience |

## Public API (Spring Boot)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/config` | Categories and counts |
| GET/POST | `/api/companies` | Manage companies |
| GET/POST | `/api/parsers` | Manage parsers |
| POST | `/api/scan` | Run scan (calls worker) |
| GET | `/api/results` | Last scan results |

## Configuration

**backend/src/main/resources/application.yml**

```yaml
worker:
  base-url: http://localhost:8001
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/fleeting_jobs
```

**worker/.env**

```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

## Notes

- Start Postgres, the Python worker, and Spring Boot before scanning.
- `OPENAI_API_KEY` lives in `worker/.env`, not in the Java backend.
- Job categories are loaded from `backend/src/main/resources/data/job_categories.json`.
