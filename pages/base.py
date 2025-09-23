from typing import Sequence, TypeVar, Generic
from typing_extensions import Self
import allure
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
)

PageT = TypeVar("PageT", bound="BasePage")


class BasePage(Generic[PageT]):
    url: str = "https://example.ru"

    def __init__(self, driver: WebDriver, timeout: int = 10) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # @allure.step("Открыть страницу: {url}")
    def open(self) -> Self:
        self.driver.get(self.url)
        return self

    # @allure.step("Найти элемент: {locator}")
    def find(self, locator: tuple[str, str]) -> WebElement:
        try:
            return self.wait.until(
                EC.presence_of_element_located(locator),
                message=f"Не удалось найти элемент: {locator}",
            )
        except TimeoutException as e:
            allure.attach(
                str(e),
                name="TimeoutException",
                attachment_type=allure.attachment_type.TEXT,
            )
            raise

    def find_all(self, locator: tuple[str, str]) -> Sequence[WebElement]:
        try:
            return self.wait.until(
                EC.presence_of_all_elements_located(locator),
                message=f"Не удалось найти элементы: {locator}",
            )
        except TimeoutException as e:
            allure.attach(
                str(e),
                name="TimeoutException",
                attachment_type=allure.attachment_type.TEXT,
            )
            raise

    # @allure.step("Клик по элементу: {locator}")
    def click(self, locator: tuple[str, str]) -> Self:
        element = self.wait.until(
            EC.element_to_be_clickable(locator),
            message=f"Не удалось кликнуть по элементу: {locator}",
        )
        try:
            element.click()
        except ElementClickInterceptedException:
            # если элемент перекрыт или вне области видимости → скроллим и пробуем снова
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )
            try:
                element.click()
            except ElementClickInterceptedException:
                ActionChains(self.driver).move_to_element(element).click().perform()
        return self

    # @allure.step("Ввести текст '{text}' в поле {locator}")
    def enter_text(self, locator: tuple[str, str], text: str) -> Self:
        element = self.find(locator)
        element.clear()
        element.send_keys(text)
        return self

    # @allure.step("Получить текст из элемента {locator}")
    def get_text(self: PageT, locator: tuple[str, str]) -> str:
        element = self.find(locator)
        return element.text
