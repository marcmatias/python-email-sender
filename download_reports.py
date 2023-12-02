import pickle
import time
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.firefox.options import Options

def remove_files_in_folder(folderPath):
    # loop through all the contents of folder
    for filename in os.listdir(folderPath):
        print(f"Removendo arquivo: \n {filename}")
        # remove the file
        os.remove(f"{folderPath}/{filename}")

def every_downloads_firefox(driver):
    if not driver.current_url.startswith("about:downloads"):
        driver.get("about:downloads")
    return driver.execute_script("""
        const items = document
            .querySelector('richlistbox')
            .querySelectorAll('richlistitem')
        const everyDownloadIsComplete = [...items].every(
            e =>!e.querySelector(".downloadDetails").value.includes("left")
        )
        if (everyDownloadIsComplete) return true
        """)

def every_downloads_chrome(driver):
    if not driver.current_url.startswith("chrome://downloads"):
        driver.get("chrome://downloads")
    return driver.execute_script("""
        const items = document.querySelector('downloads-manager')
            .shadowRoot.getElementById('downloadsList').items
        const everyDownloadIsComplete = items.every(e => e.state === "COMPLETE")
        if (everyDownloadIsComplete) return true
        """)

def select_field_and_write(elem, keys):
    elem.clear()
    if type(keys) is list:
        for key in keys:
            elem.send_keys(keys)
        return

    elem.send_keys(keys)

def element_is_clickable(driver, delay, xpath):
    WebDriverWait(driver, delay).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    xpath
                    )
                )
            )

def login(driver, email_address, password_code):
    try:
        email = driver.find_element(By.NAME, "email")
        password = driver.find_element(By.NAME, "password")
    except:
        return

    select_field_and_write(email, email_address)
    select_field_and_write(password, [password_code, Keys.RETURN ])
    # Save cookies to load user session next script run
    pickle.dump(driver.get_cookies(), open("cookies.pkl","wb"))

def download_reports(email_address, password_code):
    remove_files_in_folder('./attachments')

    options = Options()
    options.add_argument("-headless")
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", os.path.realpath('./attachments'))
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")

    driver = webdriver.Firefox(options=options)
    driver.maximize_window()
    """
        Cookie can be only add to the request with same domain.
        When webdriver init, it's request url is `data:` so you cannot add cookie to it.
        So first make a request to your url then add cookie, then request you url again.
    """
    driver.get("https://accounts.toggl.com/track/login/")

    # Load cookies
    cookies = pickle.load(open("cookies.pkl", "rb"))

    for cookie in cookies:
        driver.add_cookie(cookie)

    driver.get("https://track.toggl.com/reports")

    # Try to login if login form is the loaded page
    login(driver, email_address, password_code)

    try:
        delay = 20 # seconds

        xpath_button_this_week = "//button//span[text()='This week']"
        xpath_button_last_month = "//button[text()='Last month']"
        xpath_button_export = "//button//span[text()='Export']"
        xpath_button_download_csv = "//div//span[text()='Download CSV']"
        xpath_button_download_pdf = "//div//span[text()='Download PDF']"

        element_is_clickable(driver, delay, xpath_button_this_week)
        driver.find_element(By.XPATH, xpath_button_this_week).click()

        element_is_clickable(driver, delay, xpath_button_last_month)
        driver.find_element(By.XPATH, xpath_button_last_month).click()

        # We need to wait until report is loaded
        time.sleep(2) # seconds

        element_is_clickable(driver, delay, xpath_button_export)
        driver.find_element(By.XPATH, xpath_button_export).click()

        element_is_clickable(driver, delay, xpath_button_download_csv)
        driver.find_element(By.XPATH, xpath_button_download_csv).click()

        element_is_clickable(driver, delay, xpath_button_export)
        driver.find_element(By.XPATH, xpath_button_export).click()

        element_is_clickable(driver, delay, xpath_button_download_pdf)
        driver.find_element(By.XPATH, xpath_button_download_pdf).click()

        # We need to wait until downaload report pdf is over
        time.sleep(5) # seconds

        handles = driver.window_handles
        driver.switch_to.window(handles[1])
        driver.close()
        driver.switch_to.window(handles[0])

        # Waits for all the files to be completed and returns
        paths = WebDriverWait(driver, 120, 1).until(every_downloads_firefox)
        print("Report download ends with success!")
    except TimeoutException:
        print("Loading took too much time!")
    driver.close()

if __name__ == "__main__":
    download_reports() # need to set email_address and password_code
