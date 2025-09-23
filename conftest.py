import pytest
import allure
from typing import Any, Generator
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.remote.webdriver import WebDriver


from webdriver_manager.chrome import ChromeDriverManager


def pytest_addoption(parser):
    parser.addoption(
        "--browser", action="store", default="chrome", help="Browser: chrome"
    )
    parser.addoption(
        "--headless", action="store_true", default=False, help="Run headless"
    )


@pytest.fixture(scope="session")
def driver(request: pytest.FixtureRequest) -> Generator[WebDriver, Any, Any]:
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")

    if browser == "chrome":
        chrome_options = ChromeOptions()
        if headless:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    else:
        raise ValueError(f"Only chrome is supported in this case")

    driver.implicitly_wait(10)
    yield driver
    driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, None, None]:
    outcome = yield
    rep: pytest.TestReport = outcome.get_result()  # type: ignore

    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver")  # type: ignore
        if driver:
            try:
                png = driver.get_screenshot_as_png()
                allure.attach(
                    png,
                    name="failure_screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception as e:
                pass
