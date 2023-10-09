import sys
sys.path.append('..')

from dotenv import load_dotenv
from src import LLMScraper
from src.browser import get_browser
from src.llm import load_llm
from langchain.chat_models import ChatOpenAI

if __name__ == "__main__":
    load_dotenv()
    model_name = "mistral"

    #llm = load_llm(model_name)
    llm = ChatOpenAI()
    browser = get_browser()
    scraper = LLMScraper(llm, browser)

    output = scraper.scrape(
        url="https://www.linkedin.com/in/jordan-parker-092a7258/", 
        keys=["name", "profile", "location", "education", "experience", "skills"]
    )

    print(output)