from __future__ import annotations

import json
from typing import Any, List

from openai import OpenAI

from config import settings
from models import CompanyJobs, JobDetails, JobListing


class LLMService:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def _chat_json(self, system: str, user: str) -> dict[str, Any]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.1,
            )
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
        except json.JSONDecodeError:
            return {}
        except Exception as exc:
            raise RuntimeError(f"OpenAI request failed: {exc}") from exc

    def filter_jobs_by_categories(
        self,
        company: CompanyJobs,
        categories: List[str],
    ) -> List[JobListing]:
        if not company.jobs or not categories:
            return []

        job_summaries = [
            {"index": i, "title": job.title, "url": job.url}
            for i, job in enumerate(company.jobs)
        ]

        system = (
            "You classify job postings against target categories. "
            "Return JSON with key matched_jobs: array of objects with index (number), "
            "matched_categories (array of category strings from the provided list only). "
            "Only include jobs that clearly match at least one category."
        )
        user = (
            f"Target categories:\n{json.dumps(categories, indent=2)}\n\n"
            f"Jobs:\n{json.dumps(job_summaries, indent=2)}"
        )
        data = self._chat_json(system, user)

        matched: List[JobListing] = []
        for item in data.get("matched_jobs", []):
            idx = item.get("index")
            if idx is None or idx < 0 or idx >= len(company.jobs):
                continue
            job = company.jobs[idx]
            matched.append(
                JobListing(
                    title=job.title,
                    url=job.url,
                    matched_categories=[
                        str(c) for c in item.get("matched_categories", []) if c in categories
                    ],
                )
            )
        return matched

    def extract_job_details(
        self,
        job: JobListing,
        company_name: str,
        career_page_url: str,
        title_hint: str | None,
        description: str,
    ) -> JobDetails:
        system = (
            "You extract structured information from a job posting description. "
            "Return JSON with keys: title, required_tech_skills (array), "
            "required_soft_skills (array), location (string or null), "
            "experience_required (string summarizing years/background)."
        )
        user = (
            f"Company: {company_name}\n"
            f"Career page: {career_page_url}\n"
            f"Job URL: {job.url}\n"
            f"Job title hint: {title_hint or job.title}\n\n"
            f"Job description:\n{description}"
        )
        data = self._chat_json(system, user)

        return JobDetails(
            title=str(data.get("title") or title_hint or job.title).strip(),
            url=job.url,
            company_name=company_name,
            career_page_url=career_page_url,
            matched_categories=job.matched_categories,
            required_tech_skills=[str(s) for s in data.get("required_tech_skills", [])],
            required_soft_skills=[str(s) for s in data.get("required_soft_skills", [])],
            location=data.get("location"),
            experience_required=data.get("experience_required"),
        )
