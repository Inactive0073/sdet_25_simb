from typing import Sequence
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from typing_extensions import Self
import random

from .base import BasePage
from locators import FeedbackLocators


class FeedbackPage(BasePage):
    url = "https://practice-automation.com/form-fields/"

    def __init__(self, driver: WebDriver, timeout: int = 10) -> None:
        super().__init__(driver, timeout=timeout)

    def enter_name(self, username: str) -> Self:
        with allure.step("Ввод имени"):
            self.enter_text(FeedbackLocators.NAME_INPUT, username)
        return self

    def enter_password(self, password: str) -> Self:
        with allure.step("Ввод пароля"):
            self.enter_text(FeedbackLocators.PASSWORD_INPUT, password)
        return self

    def select_favorite_drink(self, target: Sequence[str] = ["milk", "coffee"]) -> Self:
        with allure.step("Выбор любимого напитка"):
            checkboxes: Sequence[WebElement] = self.find_all(
                FeedbackLocators.DRINK_CHECKBOXES
            )
        for checkbox in checkboxes:
            if checkbox.text.strip().lower() in target:
                checkbox.click()
        return self

    def select_favorite_color(self, target_color: str = "yellow") -> Self:
        with allure.step("Выбор любимого цвета"):
            radio_buttons = self.find_all(FeedbackLocators.COLOR_RADIO)
            for b in radio_buttons:
                if b.text.strip().lower() == target_color:
                    b.click()
        return self

    def select_automation_select(self) -> Self:
        with allure.step("Выбор инструмента автоматизации"):
            element = self.find(FeedbackLocators.AUTOMATION_SELECT)
            select = Select(element)
            choice = random.choice(
                [i for i, opt in enumerate(select.options) if opt.text.strip()]
            )
            select.select_by_index(choice)
        return self

    def enter_email(self, email: str) -> Self:
        with allure.step("Ввод email"):
            self.enter_text(FeedbackLocators.EMAIL_INPUT, email)
        return self

    def enter_message(self) -> Self:
        with allure.step("Ввод сообщения"):
            ul = self.find(FeedbackLocators.MESSAGE_UL)
            li_list = ul.find_elements(By.TAG_NAME, "li")
        len_items = str(len(li_list))
        long_word = max(*li_list, key=lambda li: len(li.text)).text
        self.enter_text(
            FeedbackLocators.MESSAGE_TEXTAREA,
            f"Количество инструментов Automation tools: {len_items}\n"
            f"Инструмент с наибольшим содержанием символов: {long_word}",
        )
        return self

    def submit(self) -> str | None:
        with allure.step("Отправка формы"):
            try:
                allure.attach(
                    self.driver.get_screenshot_as_png(),
                    name="after_submit",
                    attachment_type=allure.attachment_type.PNG,
                )
                self.click(FeedbackLocators.SUBMIT_BUTTON)
                alert = WebDriverWait(self.driver, 2).until(EC.alert_is_present())
                alert_text = alert.text
                alert.accept()
                return alert_text
            except (NoAlertPresentException, TimeoutException):
                return None
