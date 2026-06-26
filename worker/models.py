from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ScrapeRequest(BaseModel):
    url: str


class ScrapeResponse(BaseModel):
    html: str


class ParseListingRequest(BaseModel):
    html: str
    base_url: str
    listing_page: Dict[str, Any]


class JobItem(BaseModel):
    title: str
    url: str


class ParseListingResponse(BaseModel):
    jobs: List[JobItem]


class ParseJobRequest(BaseModel):
    html: str
    company_page: Dict[str, Any]


class ParseJobResponse(BaseModel):
    title: Optional[str] = None
    description: str = ""


class JobSummary(BaseModel):
    title: str
    url: str


class FilterJobsRequest(BaseModel):
    jobs: List[JobSummary]
    categories: List[str]


class MatchedJob(BaseModel):
    title: str
    url: str
    matched_categories: List[str] = Field(default_factory=list)


class FilterJobsResponse(BaseModel):
    jobs: List[MatchedJob]


class ExtractDetailsRequest(BaseModel):
    title: str
    url: str
    company_name: str
    career_page_url: str
    title_hint: Optional[str] = None
    description: str
    matched_categories: List[str] = Field(default_factory=list)


class ExtractDetailsResponse(BaseModel):
    title: str
    url: str
    company_name: str
    career_page_url: str
    matched_categories: List[str] = Field(default_factory=list)
    required_tech_skills: List[str] = Field(default_factory=list)
    required_soft_skills: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    experience_required: Optional[str] = None
