from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import CAREER_PAGES_PATH, COMPANY_PARSER_PATH, JOB_CATEGORIES_PATH, settings
from models import ScanResult
from services.pipeline import JobScanPipeline
from services.parser import load_company_parsers
from services.scraper import load_career_pages, load_job_categories


pipeline = JobScanPipeline()
scan_lock = asyncio.Lock()
scan_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(title="Fleeting Jobs API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "openai_configured": bool(settings.openai_api_key),
    }


@app.get("/api/config")
async def get_config():
    parsers = load_company_parsers(COMPANY_PARSER_PATH)
    return {
        "career_pages": load_career_pages(CAREER_PAGES_PATH),
        "categories": load_job_categories(JOB_CATEGORIES_PATH),
        "parsers": list(parsers.keys()),
    }


@app.get("/api/scan/status")
async def scan_status():
    global scan_task
    running = scan_task is not None and not scan_task.done()
    result = pipeline.last_result
    return {
        "running": running,
        "progress": pipeline.progress.model_dump(),
        "result": result.model_dump() if result else None,
    }


async def _run_scan() -> ScanResult:
    return await pipeline.run()


@app.post("/api/scan", response_model=ScanResult)
async def start_scan():
    global scan_task

    if not settings.openai_api_key:
        raise HTTPException(
            status_code=400,
            detail="OPENAI_API_KEY is not configured. Copy backend/.env.example to backend/.env",
        )

    if scan_lock.locked():
        raise HTTPException(status_code=409, detail="A scan is already running")

    async with scan_lock:
        try:
            return await _run_scan()
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/results")
async def get_results() -> Optional[ScanResult]:
    return pipeline.last_result
