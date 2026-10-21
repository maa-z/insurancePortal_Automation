import logging
from typing import Optional
from playwright.async_api import async_playwright, Playwright, Browser, Page
from ..config import settings

logger = logging.getLogger(__name__)


class PlaywrightBrowserManager:
    def __init__(self, headless: Optional[bool] = None):
        self.headless = headless if headless is not None else settings.HEADLESS
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None

    async def start(self) -> Page:
        if self._page and not self._page.is_closed():
            return self._page

        logger.info(f"Launching Playwright Chromium browser (headless={self.headless})...")
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            slow_mo=100 if not self.headless else 0,  # Slight slow_mo for smooth visual demonstration in headed mode
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await self._browser.new_context(
            viewport={"width": 1280, "height": 850}
        )
        self._page = await context.new_page()
        return self._page

    async def navigate_to_portal(self, url: Optional[str] = None) -> Page:
        page = await self.start()
        target_url = url or settings.PORTAL_BASE_URL
        logger.info(f"Navigating to Portal Simulator at {target_url}...")
        await page.goto(target_url, wait_until="networkidle")
        return page

    async def get_current_page(self) -> Optional[Page]:
        if self._page and not self._page.is_closed():
            return self._page
        return None

    async def close(self):
        try:
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception as e:
            logger.warning(f"Error during browser teardown: {e}")
        finally:
            self._page = None
            self._browser = None
            self._playwright = None
