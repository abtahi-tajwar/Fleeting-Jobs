# Fleeting Jobs

A full-stack app that scrapes company career pages, uses CSS parsers stored in PostgreSQL, filters jobs with AI, and extracts structured requirements from each listing.

## Stack

- **Frontend:** Next.js 15 (React 19)
- **Backend:** Python (FastAPI)
- **Database:** PostgreSQL (Docker)
- **Scraping:** Playwright (headless Chromium)
- **LLM:** OpenAI ChatGPT API (`gpt-4o-mini` by default)

## How it works

1. Add companies and parsers from the UI (stored in PostgreSQL)
2. Reads target job categories from `backend/data/job_categories.json`
3. Uses Playwright to scrape each company's listing URL
4. Parses job listings with company-specific CSS selectors from the database
5. Filters jobs against your categories using ChatGPT
6. Scrapes each matched job page and parses the description with CSS selectors
7. Uses ChatGPT on the description to extract title, skills, location, and experience
8. Displays results in the Jobs page with links to original postings

## Setup

### 1. Start PostgreSQL

```bash
docker compose up -d
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
```

Edit `backend/.env` and set your OpenAI API key and database URL:

```
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://fleeting:fleeting@localhost:5432/fleeting_jobs
```

Optional: seed sample RBC data:

```bash
python scripts/seed.py
```

Start the API:

```bash
uvicorn main:app --reload --port 8000
```

Tables are created automatically on startup.

### 3. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## UI

- **Top bar:** Fleeting Jobs brand + Scan jobs button
- **Sidebar:** Jobs, Companies, Parsers
- **Companies:** Add company name, listing URL, single post URL format
- **Parsers:** Select a company, paste listing page JSON and company page JSON

## Database schema

**companies**

| Column | Description |
|--------|-------------|
| id | Primary key |
| name | Company name |
| slug | URL-friendly slug |
| listing_url | Career listing page URL |
| single_post_url_format | Job post URL pattern |

**company_parsers**

| Column | Description |
|--------|-------------|
| id | Primary key |
| company_id | FK to companies |
| listing_page | JSON selector config for listing page |
| company_page | JSON selector config for job page |

## Parser JSON formats

**Listing page** (stored in `listing_page` column):

```json
{
  "job_links": {
    "selector": "a",
    "href_contains": "/job/"
  }
}
```

**Company page** (stored in `company_page` column):

```json
{
  "fields": {
    "title": ["h1", ".job-title"],
    "description": [".job-description", "main"]
  }
}
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/config` | Categories and counts |
| GET | `/api/companies` | List companies |
| POST | `/api/companies` | Create company |
| GET | `/api/parsers` | List parsers |
| POST | `/api/parsers` | Create parser |
| POST | `/api/scan` | Run full scrape + LLM pipeline |
| GET | `/api/results` | Last scan results |

## Notes

- Companies and parsers are managed from the UI and stored in PostgreSQL.
- A scan requires at least one company with a parser configured.
- Ensure Docker Postgres is running and `OPENAI_API_KEY` is set before scanning.
