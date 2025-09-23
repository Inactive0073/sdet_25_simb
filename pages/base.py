class BasePage:
    def __init__(self, browser, url) -> None:
        self.browser = browser
        self.url = url