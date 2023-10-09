import time
import structlog
from typing import List
from bs4 import BeautifulSoup
from langchain.llms import CTransformers
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from langchain.schema.messages import SystemMessage
from langchain.chains import LLMChain

from .base import BaseScraper

log = structlog.get_logger("scraper.langchain")

MODELS = {
    "llama2": ["TheBloke/Llama-2-7B-GGUF", "llama-2-7b.Q4_K_M.gguf"],
    "mistral": ["TheBloke/Mistral-7B-v0.1-GGUF", "mistral-7b-v0.1.Q4_K_M.gguf"],
    "mistral-instruct": ["a", "mistral-7b-instruct-v0.1.Q4_K_M.gguf"]
}

SYSTEM_PROMPT = """
    You are a webscraping assistant. You are to receive HTML or raw text and extract the JSON records that satisfuy the users prompt.
"""
MESSAGE_PROMPT = """
    Given the following input, please extract the JSON records that satisfy the users prompt.
    Input
    ---
    {input}
    ---
    Required Metadata Keys
    ---
    {metadata}
    ---
    Return only a valid JSON and nothing else. The JSON should contain all the keys in the metadata. If an item is not found, return null for the value.
"""

LLAMA_PROMPT = """<<SYS>>
You are a webscraping assistant. You are to receive HTML or raw text and extract the JSON records that satisfuy the users prompt.
<</SYS>>

[INST] 
Given the following input, please extract the JSON records that satisfy the users prompt.
Input
---
{input}
---
Required Metadata Keys
---
{metadata}
---
Return only a valid JSON and nothing else. The JSON should contain all the keys in the metadata. If an item is not found, return null for the value.
[/INST]"""

# TODO:
# 1. Use langchain document loaders for HTML increase integration


class LLMScraper(BaseScraper):
    def __init__(self, llm, browser, config):
        super().__init__(browser, config)
        self.llm = llm
        if isinstance(llm, CTransformers):
            prompt = PromptTemplate.from_template(LLAMA_PROMPT)
        else:
            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessagePromptTemplate.from_template(MESSAGE_PROMPT),
                ]
            )
        self.chain = LLMChain(llm=llm, prompt=prompt)

    @property
    def html(self):
        html = BeautifulSoup(self.browser.page_source, "lxml")
        log.debug("html", data=html)
        return html
    

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
    
    # should change this to take a JSON schema or pydantic class as well
    # could look at langchain pydantic output parsers to do this
    def scrape(self, url: str, keys: str, wait=0):
        """A method for scraping a page."""
        self.load_page(url, wait)
        text = self.html.find("body").get_text(separator=' ')
        return self.extract(text, keys)

    # need to develop a way to deal with larger contexts performatively
    # also need to evaluate the performance of html vs raw text as input
    def extract(self, text: str, metadata: List[str]):
        """A method for extracting data from text."""
        log.info("running llm to extract", metadata=metadata)
        return self.chain({ "input": text, "metadata": metadata })

def load_llm(model_name: str):
    llm = CTransformers(
        model=MODELS[model_name][0], 
        model_file=MODELS[model_name][1],
        model_type='llama', 
        stream=True, 
        gpu_layers=0,
        verbose=True,
    )
    return llm