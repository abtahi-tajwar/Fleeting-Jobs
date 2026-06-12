from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from repositories.companies import (
    create_company,
    create_parser,
    get_company,
    get_parser_for_company,
    list_companies,
    list_parsers,
)
from schemas import (
    CompanyCreate,
    CompanyParserCreate,
    CompanyParserResponse,
    CompanyResponse,
)

router = APIRouter(prefix="/api/companies", tags=["companies"])
parser_router = APIRouter(prefix="/api/parsers", tags=["parsers"])


def _company_response(company) -> CompanyResponse:
    return CompanyResponse(
        id=company.id,
        name=company.name,
        slug=company.slug,
        listing_url=company.listing_url,
        single_post_url_format=company.single_post_url_format,
        has_parser=company.parser is not None,
    )


@router.get("", response_model=List[CompanyResponse])
def get_companies(db: Session = Depends(get_db)):
    return [_company_response(company) for company in list_companies(db)]


@router.post("", response_model=CompanyResponse, status_code=201)
def add_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    company = create_company(
        db,
        payload.name,
        payload.listing_url,
        payload.single_post_url_format,
    )
    return _company_response(company)


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company_by_id(company_id: int, db: Session = Depends(get_db)):
    company = get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return _company_response(company)


def _parser_response(parser) -> CompanyParserResponse:
    return CompanyParserResponse(
        id=parser.id,
        company_id=parser.company_id,
        listing_page=parser.listing_page,
        company_page=parser.company_page,
        company_name=parser.company.name if parser.company else None,
    )


@parser_router.get("", response_model=List[CompanyParserResponse])
def get_parsers(db: Session = Depends(get_db)):
    return [_parser_response(parser) for parser in list_parsers(db)]


@parser_router.post("", response_model=CompanyParserResponse, status_code=201)
def add_parser(payload: CompanyParserCreate, db: Session = Depends(get_db)):
    try:
        create_parser(
            db,
            payload.company_id,
            payload.listing_page,
            payload.company_page,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    parser = get_parser_for_company(db, payload.company_id)
    if not parser:
        raise HTTPException(status_code=500, detail="Failed to load created parser")
    return _parser_response(parser)
