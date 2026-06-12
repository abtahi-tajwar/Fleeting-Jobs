from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session, joinedload

from db.models import Company, CompanyParser
from utils import slugify


def list_companies(db: Session) -> List[Company]:
    return (
        db.query(Company)
        .options(joinedload(Company.parser))
        .order_by(Company.name.asc())
        .all()
    )


def get_company(db: Session, company_id: int) -> Optional[Company]:
    return (
        db.query(Company)
        .options(joinedload(Company.parser))
        .filter(Company.id == company_id)
        .first()
    )


def create_company(
    db: Session,
    name: str,
    listing_url: str,
    single_post_url_format: str,
) -> Company:
    base_slug = slugify(name)
    slug = base_slug
    suffix = 1
    while db.query(Company).filter(Company.slug == slug).first():
        slug = f"{base_slug}-{suffix}"
        suffix += 1

    company = Company(
        name=name.strip(),
        slug=slug,
        listing_url=listing_url.strip(),
        single_post_url_format=single_post_url_format.strip(),
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def list_companies_with_parsers(db: Session) -> List[Company]:
    return (
        db.query(Company)
        .join(CompanyParser)
        .options(joinedload(Company.parser))
        .order_by(Company.name.asc())
        .all()
    )


def list_parsers(db: Session) -> List[CompanyParser]:
    return (
        db.query(CompanyParser)
        .options(joinedload(CompanyParser.company))
        .order_by(CompanyParser.id.asc())
        .all()
    )


def get_parser_for_company(db: Session, company_id: int) -> Optional[CompanyParser]:
    return (
        db.query(CompanyParser)
        .options(joinedload(CompanyParser.company))
        .filter(CompanyParser.company_id == company_id)
        .first()
    )


def create_parser(
    db: Session,
    company_id: int,
    listing_page: Dict[str, Any],
    company_page: Dict[str, Any],
) -> CompanyParser:
    company = get_company(db, company_id)
    if not company:
        raise ValueError(f"Company with id {company_id} not found")
    if company.parser:
        raise ValueError(f"Parser already exists for company '{company.name}'")

    parser = CompanyParser(
        company_id=company_id,
        listing_page=listing_page,
        company_page=company_page,
    )
    db.add(parser)
    db.commit()
    db.refresh(parser)
    return parser
