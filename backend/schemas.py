from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    listing_url: str = Field(min_length=1)
    single_post_url_format: str = Field(min_length=1)


class CompanyResponse(BaseModel):
    id: int
    name: str
    slug: str
    listing_url: str
    single_post_url_format: str
    has_parser: bool = False

    model_config = {"from_attributes": True}


class CompanyParserCreate(BaseModel):
    company_id: int
    listing_page: Dict[str, Any]
    company_page: Dict[str, Any]


class CompanyParserResponse(BaseModel):
    id: int
    company_id: int
    listing_page: Dict[str, Any]
    company_page: Dict[str, Any]
    company_name: Optional[str] = None

    model_config = {"from_attributes": True}


class AppConfigResponse(BaseModel):
    categories: List[str]
    company_count: int
    parser_count: int
