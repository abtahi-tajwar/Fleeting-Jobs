# Fleeting Jobs

A full-stack app that scrapes company career pages, uses OpenAI to identify relevant job postings, and extracts structured requirements from each listing.

## Stack

- **Frontend:** Next.js 15 (React 19)
- **Backend:** Python (FastAPI)
- **Scraping:** Playwright (headless Chromium)
- **LLM:** OpenAI ChatGPT API (`gpt-4o-mini` by default)

## How it works

1. Reads career page URLs from `backend/data/career_pages.json`
2. Reads per-company HTML parsers from `backend/data/company_parser.json`
3. Reads target job categories from `backend/data/job_categories.json`
4. Uses Playwright to scrape each career page HTML
5. Parses job listings with CSS selectors defined in `company_parser.json`
6. Filters jobs against your categories using ChatGPT
7. Scrapes each matched job page and parses the description with CSS selectors
8. Uses ChatGPT on the description to extract:
   - Job title
   - Required tech skills
   - Required soft skills
   - Location
   - Experience / background required
9. Displays results in the Next.js UI with links to original postings

## Setup

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
```

Edit `backend/.env` and set your OpenAI API key:

```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

Replace the sample JSON files with your own:

- `backend/data/career_pages.json`
- `backend/data/company_parser.json`
- `backend/data/job_categories.json`

Start the API:

```bash
uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## JSON file formats

**career_pages.json**

```json
{
  "career_pages": [
    { "name": "RBC", "url": "https://jobs.rbc.com/ca/en/c/technology-analytics-research-jobs" }
  ]
}
```

The `name` must match a key in `company_parser.json`.

**company_parser.json**

```json
{
  "RBC": {
    "listing_page": {
      "job_links": {
        "selector": "a",
        "href_contains": "/job/"
      }
    },
    "job_page": {
      "fields": {
        "title": ["h1", ".job-title"],
        "description": [".job-description", "main"]
      }
    }
  }
}
```

**job_categories.json**

```json
{
  "categories": [
    "Software Engineering",
    "Machine Learning / AI"
  ]
}
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/config` | Loaded career pages and categories |
| POST | `/api/scan` | Run full scrape + LLM pipeline |
| GET | `/api/results` | Last scan results |

## Notes

- A full scan can take several minutes depending on the number of career pages and matched jobs (each page requires browser navigation + LLM calls).
- Replace the sample URLs in `career_pages.json` with your target companies before running.
- Ensure `OPENAI_API_KEY` is set; the scan will fail without it.
