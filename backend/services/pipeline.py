from __future__ import annotations

from typing import List, Optional, Tuple

from config import CAREER_PAGES_PATH, COMPANY_PARSER_PATH, JOB_CATEGORIES_PATH
from models import CompanyJobs, JobDetails, JobListing, ScanProgress, ScanResult
from services.llm import LLMService
from services.parser import get_company_parser, load_company_parsers, parse_job_listing_page, parse_job_page
from services.scraper import (
    BrowserScraper,
    load_career_pages,
    load_job_categories,
)


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

    async def run(self) -> ScanResult:
        self.llm = LLMService()

        career_pages = load_career_pages(CAREER_PAGES_PATH)
        categories = load_job_categories(JOB_CATEGORIES_PATH)
        parsers = load_company_parsers(COMPANY_PARSER_PATH)

        companies: List[CompanyJobs] = []
        detailed_jobs: List[JobDetails] = []

        total_steps = len(career_pages)
        self._set_progress("running", "Starting scan", 0, total_steps)

        await self.scraper.start()
        try:
            matched_jobs: List[Tuple[CompanyJobs, JobListing]] = []

            for index, page in enumerate(career_pages, start=1):
                url = page["url"]
                company_name = page.get("name") or "Unknown Company"
                self._set_progress(
                    "running",
                    f"Parsing job listings: {company_name}",
                    index - 1,
                    total_steps,
                )

                try:
                    parser_config = get_company_parser(parsers, company_name)
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
                        matched_jobs.append((company, job))
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

            for job_index, (company, job) in enumerate(matched_jobs, start=1):
                self._set_progress(
                    "running",
                    f"Analyzing job: {job.title}",
                    job_index - 1,
                    job_total,
                )
                try:
                    parser_config = get_company_parser(parsers, company.company_name)
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
