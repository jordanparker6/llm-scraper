from seleniumbase import Driver

def get_browser(headless: bool = True):
    return Driver(uc=True, headless=headless)