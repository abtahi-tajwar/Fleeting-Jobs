from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from config import JOB_CATEGORIES_PATH
from database import SessionLocal
from models import CompanyJobs, JobDetails, JobListing, ScanProgress, ScanResult
from repositories.companies import list_companies_with_parsers
from services.llm import LLMService
from services.parser import build_parser_config, parse_job_listing_page, parse_job_page
from services.scraper import BrowserScraper, load_job_categories


class JobScanPipeline:
    def __init__(self) -> None:
        self.llm: Optional[LLMService] = None
        self.scraper = BrowserScraper()
        self._progress = ScanProgress(status="idle", message="Ready", current=0, total=0)
        self._last_result: Optional[ScanResult] = None

    @property
    def progress(self) -> ScanProgress:
        return self._progress

    @property
    def last_result(self) -> Optional[ScanResult]:
        return self._last_result

    def _set_progress(self, status: str, message: str, current: int = 0, total: int = 0) -> None:
        self._progress = ScanProgress(
            status=status,
            message=message,
            current=current,
            total=total,
        )

    def _load_scan_targets(self, db: Session):
        companies = list_companies_with_parsers(db)
        if not companies:
            raise ValueError(
                "No companies with parsers configured. Add a company and parser from the UI first."
            )
        return companies

    async def run(self) -> ScanResult:
        self.llm = LLMService()
        categories = load_job_categories(JOB_CATEGORIES_PATH)

        db = SessionLocal()
        try:
            scan_targets = self._load_scan_targets(db)
        finally:
            db.close()

        companies: List[CompanyJobs] = []
        detailed_jobs: List[JobDetails] = []

        total_steps = len(scan_targets)
        self._set_progress("running", "Starting scan", 0, total_steps)

        await self.scraper.start()
        try:
            matched_jobs: List[Tuple[CompanyJobs, JobListing, dict]] = []

            for index, company_row in enumerate(scan_targets, start=1):
                company_name = company_row.name
                url = company_row.listing_url
                parser_config = build_parser_config(
                    company_row.parser.listing_page,
                    company_row.parser.company_page,
                )

                self._set_progress(
                    "running",
                    f"Parsing job listings: {company_name}",
                    index - 1,
                    total_steps,
                )

                try:
                    html = await self.scraper.scrape_career_page_html(url)
                    raw_jobs = parse_job_listing_page(html, parser_config, url)

                    company = CompanyJobs(
                        company_name=company_name,
                        career_page_url=url,
                        jobs=[
                            JobListing(title=job["title"], url=job["url"])
                            for job in raw_jobs
                            if job.get("title") and job.get("url")
                        ],
                    )
                    company.jobs = self.llm.filter_jobs_by_categories(company, categories)
                    companies.append(company)

                    for job in company.jobs:
                        matched_jobs.append((company, job, parser_config))
                except Exception as exc:
                    companies.append(
                        CompanyJobs(
                            company_name=company_name,
                            career_page_url=url,
                            error=str(exc),
                        )
                    )

            job_total = len(matched_jobs)
            self._set_progress("running", "Scraping matched job descriptions", 0, job_total)

            for job_index, (company, job, parser_config) in enumerate(matched_jobs, start=1):
                self._set_progress(
                    "running",
                    f"Analyzing job: {job.title}",
                    job_index - 1,
                    job_total,
                )
                try:
                    html = await self.scraper.scrape_job_page_html(job.url)
                    parsed = parse_job_page(html, parser_config)

                    description = parsed.get("description") or ""
                    if not description.strip():
                        raise ValueError("Could not extract job description from page")

                    details = self.llm.extract_job_details(
                        job,
                        company.company_name,
                        company.career_page_url,
                        parsed.get("title"),
                        description,
                    )
                    detailed_jobs.append(details)
                except Exception as exc:
                    detailed_jobs.append(
                        JobDetails(
                            title=job.title,
                            url=job.url,
                            company_name=company.company_name,
                            career_page_url=company.career_page_url,
                            matched_categories=job.matched_categories,
                            error=str(exc),
                        )
                    )
        finally:
            await self.scraper.stop()

        result = ScanResult(
            status="completed",
            companies=companies,
            jobs=detailed_jobs,
            progress=ScanProgress(
                status="completed",
                message="Scan completed",
                current=total_steps,
                total=total_steps,
            ),
        )
        self._last_result = result
        self._progress = result.progress or ScanProgress(status="completed", message="Done")
        return result
