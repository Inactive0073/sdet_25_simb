from selenium.webdriver.remote.webdriver import WebDriver

from pages.login import LoginPage


def test_fill_login_form(driver: WebDriver):
    login_page = LoginPage(driver)
    login_page.open().enter_name("John Doe")
