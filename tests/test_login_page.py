from selenium.webdriver.remote.webdriver import WebDriver

from pages.feedback import FeedbackPage


def test_fill_login_form(driver: WebDriver):
    feedback_page = FeedbackPage(driver)
    (
        feedback_page.open()
        .enter_name("Sim Bir Soft")
        .enter_password("Rjf321isad!")
        .select_favorit_drink()
        .select_favorite_color()
        .select_automation_select()
        .enter_email("good@email.simb")
        .enter_message()
        .submit()
    )
