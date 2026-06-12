#!/usr/bin/env python3
"""Seed the database with sample RBC company and parser data."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database import SessionLocal, init_db
from repositories.companies import create_company, create_parser, list_companies


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        existing = list_companies(db)
        if existing:
            print("Database already has companies; skipping seed.")
            return

        company = create_company(
            db,
            name="RBC",
            listing_url="https://jobs.rbc.com/ca/en/c/technology-analytics-research-jobs",
            single_post_url_format="https://jobs.rbc.com/ca/en/job/{id}",
        )
        create_parser(
            db,
            company.id,
            listing_page={
                "job_links": {
                    "selector": "a",
                    "href_contains": "/job/",
                }
            },
            company_page={
                "fields": {
                    "title": ["h1", ".job-title"],
                    "description": [
                        ".job-description",
                        "[data-testid='job-description']",
                        "main",
                    ],
                }
            },
        )
        print("Seeded RBC company and parser.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
