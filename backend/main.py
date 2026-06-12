from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from config import JOB_CATEGORIES_PATH, settings
from database import get_db, init_db
from models import ScanResult
from repositories.companies import list_companies, list_parsers
from routers.companies import parser_router, router as companies_router
from schemas import AppConfigResponse
from services.pipeline import JobScanPipeline
from services.scraper import load_job_categories


pipeline = JobScanPipeline()
scan_lock = asyncio.Lock()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Fleeting Jobs API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(companies_router)
app.include_router(parser_router)


@app.get("/api/health")
async def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    return {
        "status": "ok",
        "openai_configured": bool(settings.openai_api_key),
        "database_connected": db_connected,
    }


@app.get("/api/config", response_model=AppConfigResponse)
async def get_config(db: Session = Depends(get_db)):
    companies = list_companies(db)
    parsers = list_parsers(db)
    return AppConfigResponse(
        categories=load_job_categories(JOB_CATEGORIES_PATH),
        company_count=len(companies),
        parser_count=len(parsers),
    )


@app.get("/api/scan/status")
async def scan_status():
    running = scan_lock.locked()
    result = pipeline.last_result
    return {
        "running": running,
        "progress": pipeline.progress.model_dump(),
        "result": result.model_dump() if result else None,
    }


@app.post("/api/scan", response_model=ScanResult)
async def start_scan():
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=400,
            detail="OPENAI_API_KEY is not configured. Copy backend/.env.example to backend/.env",
        )

    if scan_lock.locked():
        raise HTTPException(status_code=409, detail="A scan is already running")

    async with scan_lock:
        try:
            return await pipeline.run()
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/results")
async def get_results() -> Optional[ScanResult]:
    return pipeline.last_result
