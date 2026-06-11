from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def load_company_parsers(path: Path) -> Dict[str, dict]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("company_parser.json must be an object keyed by company name")
    return data


def get_company_parser(parsers: Dict[str, dict], company_name: str) -> dict:
    if company_name not in parsers:
        available = ", ".join(sorted(parsers.keys())) or "(none)"
        raise ValueError(
            f"No parser configured for company '{company_name}'. "
            f"Available parsers: {available}"
        )
    return parsers[company_name]


def parse_job_listing_page(html: str, config: dict, base_url: str) -> List[dict]:
    soup = BeautifulSoup(html, "html.parser")

    job_links = config["listing_page"]["job_links"]
    selector = job_links["selector"]
    href_contains = job_links["href_contains"]

    jobs: List[dict] = []
    seen: set[str] = set()

    for element in soup.select(selector):
        href = element.get("href")
        if not href:
            continue
        if href_contains not in href:
            continue

        url = urljoin(base_url, href)
        if url in seen:
            continue

        seen.add(url)
        jobs.append({
            "title": element.get_text(strip=True),
            "url": url,
        })

    return jobs


def extract_field(soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            return element.get_text(" ", strip=True)
    return None


def extract_description(soup: BeautifulSoup, selectors: List[str]) -> str:
    best_text = ""
    for selector in selectors:
        for element in soup.select(selector):
            text = element.get_text(" ", strip=True)
            if len(text) > len(best_text):
                best_text = text
    return best_text


def parse_job_page(html: str, config: dict) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    fields = config["job_page"]["fields"]

    return {
        "title": extract_field(soup, fields["title"]),
        "description": extract_description(soup, fields["description"]),
    }
