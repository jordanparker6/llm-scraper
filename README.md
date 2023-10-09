# llm-scraper

A webscraper that leverages a LLM for HTML parsing.

The goal is to build a bot that can traverse a website and collect all the required information it is instructed to collect.

The bot must:

1. be robust so that it doesn't need to be informed of CSS Selector rules to parse the incoming HTML
2. it must be able to adapt to changing HTML; and,
3. it must adhere to rate limiting policies.

To do this, we will need to headless browsers and a local quantised LLM. We are adopting langchain as the LLM API.

Research:

1. Look at libraries like scrapy for guidance
2. Look at service providers like scrapingbee
