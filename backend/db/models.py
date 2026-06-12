from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    pass


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    listing_url: Mapped[str] = mapped_column(Text, nullable=False)
    single_post_url_format: Mapped[str] = mapped_column(Text, nullable=False)

    parser: Mapped[Optional["CompanyParser"]] = relationship(
        "CompanyParser",
        back_populates="company",
        uselist=False,
        cascade="all, delete-orphan",
    )


class CompanyParser(Base):
    __tablename__ = "company_parsers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    listing_page: Mapped[dict] = mapped_column(JSONB, nullable=False)
    company_page: Mapped[dict] = mapped_column(JSONB, nullable=False)

    company: Mapped["Company"] = relationship("Company", back_populates="parser")
