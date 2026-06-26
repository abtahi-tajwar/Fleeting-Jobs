from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from models import (
    ExtractDetailsRequest,
    ExtractDetailsResponse,
    FilterJobsRequest,
    FilterJobsResponse,
    ParseJobRequest,
    ParseJobResponse,
    ParseListingRequest,
    ParseListingResponse,
    ScrapeRequest,
    ScrapeResponse,
)
from services.llm import LLMService
from services.parser import parse_job_listing_page, parse_job_page
from services.scraper import BrowserScraper

scraper = BrowserScraper()
llm: LLMService | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global llm
    await scraper.start()
    if settings.openai_api_key:
        llm = LLMService()
    yield
    await scraper.stop()


app = FastAPI(title="Fleeting Jobs Worker", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "openai_configured": bool(settings.openai_api_key),
    }


@app.post("/scrape", response_model=ScrapeResponse)
async def scrape(request: ScrapeRequest):
    html = await scraper.scrape(request.url)
    return ScrapeResponse(html=html)


@app.post("/parse/listing", response_model=ParseListingResponse)
def parse_listing(request: ParseListingRequest):
    jobs = parse_job_listing_page(request.html, request.listing_page, request.base_url)
    return ParseListingResponse(jobs=jobs)


@app.post("/parse/job", response_model=ParseJobResponse)
def parse_job(request: ParseJobRequest):
    parsed = parse_job_page(request.html, request.company_page)
    return ParseJobResponse(
        title=parsed.get("title"),
        description=parsed.get("description") or "",
    )


def _require_llm() -> LLMService:
    if llm is None:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY is not configured")
    return llm


@app.post("/llm/filter-jobs", response_model=FilterJobsResponse)
def filter_jobs(request: FilterJobsRequest):
    service = _require_llm()
    jobs = [job.model_dump() for job in request.jobs]
    matched = service.filter_jobs_by_categories(jobs, request.categories)
    return FilterJobsResponse(jobs=matched)


@app.post("/llm/extract-details", response_model=ExtractDetailsResponse)
def extract_details(request: ExtractDetailsRequest):
    service = _require_llm()
    return service.extract_job_details(
        request.title,
        request.url,
        request.company_name,
        request.career_page_url,
        request.title_hint,
        request.description,
        request.matched_categories,
    )
