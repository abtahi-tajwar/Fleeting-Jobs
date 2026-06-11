from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.async_api import Browser, Page, async_playwright


MAX_PAGE_TEXT_CHARS = 120_000
MAX_JOB_TEXT_CHARS = 80_000


def _clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n[Content truncated for processing]"


async def _wait_for_page(page: Page) -> None:
    try:
        await page.wait_for_load_state("networkidle", timeout=15_000)
    except Exception:
        await page.wait_for_load_state("domcontentloaded")


async def scrape_page_html(browser: Browser, url: str) -> str:
    page = await browser.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
        await _wait_for_page(page)
        return await page.content()
    finally:
        await page.close()


async def scrape_url(browser: Browser, url: str) -> str:
    page = await browser.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
        await _wait_for_page(page)
        html = await page.content()
        text = _clean_text(html)
        return _truncate(text, MAX_PAGE_TEXT_CHARS)
    finally:
        await page.close()


async def scrape_job_url(browser: Browser, url: str) -> str:
    page = await browser.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
        await _wait_for_page(page)
        html = await page.content()
        text = _clean_text(html)
        return _truncate(text, MAX_JOB_TEXT_CHARS)
    finally:
        await page.close()


class BrowserScraper:
    def __init__(self) -> None:
        self._playwright = None
        self._browser: Browser | None = None

    async def start(self) -> None:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)

    async def stop(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def scrape_career_page_html(self, url: str) -> str:
        if not self._browser:
            raise RuntimeError("Browser scraper is not started")
        return await scrape_page_html(self._browser, url)

    async def scrape_job_page_html(self, url: str) -> str:
        if not self._browser:
            raise RuntimeError("Browser scraper is not started")
        return await scrape_page_html(self._browser, url)

    async def scrape_career_page(self, url: str) -> str:
        if not self._browser:
            raise RuntimeError("Browser scraper is not started")
        return await scrape_url(self._browser, url)

    async def scrape_job_page(self, url: str) -> str:
        if not self._browser:
            raise RuntimeError("Browser scraper is not started")
        return await scrape_job_url(self._browser, url)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_career_pages(path: Path) -> list[dict]:
    data = load_json(path)
    pages = data.get("career_pages", data)
    if isinstance(pages, list):
        return pages
    raise ValueError("career_pages.json must contain a list or a 'career_pages' array")


def load_job_categories(path: Path) -> list[str]:
    data = load_json(path)
    categories = data.get("categories", data)
    if isinstance(categories, list):
        return [str(c) for c in categories]
    raise ValueError("job_categories.json must contain a list or a 'categories' array")
