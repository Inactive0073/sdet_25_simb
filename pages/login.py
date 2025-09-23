from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from typing_extensions import Self

from .base import BasePage


class LoginPage(BasePage):
    url = "https://practice-automation.com/form-fields/"

    def __init__(self, driver: WebDriver, timeout: int = 10) -> None:
        super().__init__(driver, timeout=timeout)

    def enter_name(self, username: str) -> Self:
        self.enter_text((By.XPATH, "//input[@name='name-input']"), username)
        return self

    def enter_password(self, password: str) -> Self:
        self.enter_text((By.NAME, "password"), password)
        return self

    def submit(self) -> Self:
        self.click((By.NAME, "submit"))
        return self
