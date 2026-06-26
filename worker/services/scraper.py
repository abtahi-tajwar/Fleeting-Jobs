from __future__ import annotations

from playwright.async_api import Browser, Page, async_playwright


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

    async def scrape(self, url: str) -> str:
        if not self._browser:
            raise RuntimeError("Browser scraper is not started")
        return await scrape_page_html(self._browser, url)
