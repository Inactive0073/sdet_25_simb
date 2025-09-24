from selenium.webdriver.common.by import By


class FeedbackLocators:
    NAME_INPUT = (By.XPATH, "//input[@name='name-input']")
    PASSWORD_INPUT = (
        By.XPATH,
        "//form[@id='feedbackForm']/label/input[@type='password']",
    )
    DRINK_CHECKBOXES = (By.XPATH, "//label[contains(@for, 'drink')]")
    COLOR_RADIO = (By.CSS_SELECTOR, "input[type='radio'] + label")
    AUTOMATION_SELECT = (By.ID, "automation")
    EMAIL_INPUT = (By.ID, "email")
    MESSAGE_TEXTAREA = (By.ID, "message")
    MESSAGE_UL = (
        By.XPATH,
        "//label[contains(text(), 'Automation tools')]/following-sibling::ul",
    )
    SUBMIT_BUTTON = (By.ID, "submit-btn")
