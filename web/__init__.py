"""Web interfacing tools for soclib"""

from selenium import webdriver

def get_screenshot(url: str, timeout=10) -> str:
    """Get a screenshot of a website using Selenium and return it as a base64 encoded image

    Args:
        url (str): The URL of the website to screenshot
        timeout (int, optional): The number of seconds to wait before timing out. Defaults to 10.

    Returns:
        str: The base64 encoded image
    """

    # Initialize the webdriver in headless mode
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options, service_log_path='/dev/null')

    # Open the website and wait for it to load or timeout
    driver.set_page_load_timeout(timeout)
    driver.get(url)

    # Take a screenshot and return base64 encoded image
    screenshot =  driver.get_screenshot_as_base64()

    # Close the webdriver
    driver.quit()

    return screenshot
