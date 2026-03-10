from typing import Sequence
import allure
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from src.pages.feedback import FeedbackPage


@allure.epic("UI Tests")
@allure.feature("Feedback Form")
@allure.story("Positive")
@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.parametrize(
    ("drinks", "color"),
    [
        (["milk", "coffee"], "yellow"),
    ],
)
def test_fill_feedback_form(driver: WebDriver, drinks: Sequence[str], color: str):
    """Позитивный сценарий: форма заполняется корректно → ожидаем Message received!"""

    feedback_page = FeedbackPage(driver)
    alert_text = (
        feedback_page.open()
        .enter_name("Sim Bir Soft")
        .enter_password("Rjf321isad!")
        .select_favorite_drink(drinks)
        .select_favorite_color(color)
        .select_automation_select()
        .enter_email("good@email.simb")
        .enter_message()
        .submit()
    )
    assert alert_text == "Message received!", f"Unexpected alert message: {alert_text}"


@allure.epic("UI Tests")
@allure.feature("Feedback Form")
@allure.story("Negative")
@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.parametrize(
    ("drinks", "color"),
    [
        (["milk", "coffee"], "yellow"),
    ],
)
def test_fill_feedback_form_invalid_email(
    driver: WebDriver, drinks: Sequence[str], color: str
):
    """Негативный сценарий: невалидный email, пустое поле имени → форма не должна пройти валидацию"""
    feedback_page = FeedbackPage(driver)
    alert_text = (
        feedback_page.open()
        .enter_name("")
        .enter_password("akapass")
        .select_favorite_drink(drinks)
        .select_favorite_color(color)
        .select_automation_select()
        .enter_email("bad-email")
        .enter_message()
        .submit()
    )
    assert alert_text is None or alert_text != "Message received!", (
        f"Unexpected positive alert message: {alert_text}"
    )
