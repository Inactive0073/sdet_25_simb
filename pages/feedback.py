from typing import Sequence
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoAlertPresentException
from typing_extensions import Self
import random

from .base import BasePage


class FeedbackPage(BasePage):
    url = "https://practice-automation.com/form-fields/"

    def __init__(self, driver: WebDriver, timeout: int = 10) -> None:
        super().__init__(driver, timeout=timeout)

    def enter_name(self, username: str) -> Self:
        self.enter_text((By.XPATH, "//input[@name='name-input']"), username)
        return self

    def enter_password(self, password: str) -> Self:
        self.enter_text(
            (By.XPATH, "//form[@id='feedbackForm']/label/input[@type='password']"),
            password,
        )
        return self

    def select_favorit_drink(self, target: list[str] = ["milk", "coffee"]) -> Self:
        checkboxes: Sequence[WebElement] = self.find_all(
            (By.XPATH, "//label[contains(@for, 'drink')]")
        )
        for checkbox in checkboxes:
            if checkbox.text.strip().lower() in target:
                checkbox.click()
        return self

    def select_favorite_color(self, target_color: str = "yellow") -> Self:
        radio_buttons = self.find_all((By.CSS_SELECTOR, "input[type='radio'] + label"))
        for b in radio_buttons:
            if b.text.strip().lower() == target_color:
                b.click()
        return self

    def select_automation_select(self) -> Self:
        element = self.find((By.ID, "automation"))
        select = Select(element)
        choice = random.choice(
            [i for i, opt in enumerate(select.options) if opt.text.strip()]
        )
        select.select_by_index(choice)
        return self

    def enter_email(self, email: str) -> Self:
        self.enter_text((By.ID, "email"), email)
        return self

    def enter_message(self) -> Self:
        ul = self.find(
            (
                By.XPATH,
                "//label[contains(text(), 'Automation tools')]/following-sibling::ul",
            )
        )
        len_items = str(len(ul.find_elements(By.TAG_NAME, "li")))
        self.enter_text((By.ID, "message"), len_items)
        return self

    def submit(self) -> Self:
        self.click((By.ID, "submit-btn"))

        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            assert alert_text == "Message received!", (
                f"Unexpected alert text: {alert_text}"
            )
        except NoAlertPresentException:
            raise AssertionError("Alert did not appear after submit")

        return self
