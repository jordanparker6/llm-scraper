import time
import structlog
import os
from abc import ABC
from bs4 import BeautifulSoup
from pydantic import BaseModel
from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_random_exponential

log = structlog.get_logger("scraper.base")

# TODO:
# 1. Add a method to automatically crawl through the pages of a website.
# 2. Add a method to automatically download files from a website.
# 3. Add a way to manage metadata and downloaded artefacts for each page.

class ScraperConfig(BaseModel):
    json_logs: bool = False
    level: str = "INFO"
    file: str = ".logs/scraper.log"
    root_dir: str = "."
    log_html: bool = True

    @classmethod
    def from_env(cls):
        from dotenv import load_dotenv

        load_dotenv()
        return ScraperConfig(
            download_formats=["pdf"],
            json_logs=os.getenv("JSON_LOGS", False),
            level=os.getenv("LOG_LEVEL", "INFO"),
            file=os.getenv("LOG_FILE", ".logs/scraper.log"),
            root_dir=os.getenv("ROOT_DIR", "."),
            log_html=os.getenv("LOG_HTML", True),
        )

class BaseScraper(ABC):
    """A base web scraper class that initiates the driver."""

    def __init__(
        self,
        browser,
        config: ScraperConfig,
    ):
        self.browser = browser
        self.config = config

    @property
    def html(self):
        html = BeautifulSoup(self.browser.page_source, "lxml")
        if self.config.log_html:
            log.debug("logging html", data=html, url=self.browser.current_url)
        return html

    @retry(wait=wait_random_exponential(min=10, max=60), stop=stop_after_attempt(3))
    def load_page(self, url: str, wait=0):
        self.browser.get(url)
        time.sleep(wait)
        return self

    def scroll_down(self):
        """A method for scrolling the page."""
        last_height = self.browser.execute_script("return document.body.scrollHeight")

        while True:
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
