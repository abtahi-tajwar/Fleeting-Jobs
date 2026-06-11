from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class CareerPage(BaseModel):
    name: Optional[str] = None
    url: str


class JobListing(BaseModel):
    title: str
    url: str
    matched_categories: List[str] = Field(default_factory=list)


class CompanyJobs(BaseModel):
    company_name: str
    career_page_url: str
    jobs: List[JobListing] = Field(default_factory=list)
    error: Optional[str] = None


class JobDetails(BaseModel):
    title: str
    url: str
    company_name: str
    career_page_url: str
    matched_categories: List[str] = Field(default_factory=list)
    required_tech_skills: List[str] = Field(default_factory=list)
    required_soft_skills: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    experience_required: Optional[str] = None
    error: Optional[str] = None


class ScanProgress(BaseModel):
    status: str
    message: str
    current: int = 0
    total: int = 0


class ScanResult(BaseModel):
    status: str
    companies: List[CompanyJobs] = Field(default_factory=list)
    jobs: List[JobDetails] = Field(default_factory=list)
    progress: Optional[ScanProgress] = None
    error: Optional[str] = None
