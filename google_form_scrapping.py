import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, NoSuchWindowException
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from time import sleep
from selenium.webdriver.chrome.options import Options

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CustomChrome(uc.Chrome):
    def __del__(self):
        """Override destructor if needed to ensure proper cleanup"""
        pass  

class GoogleFormAutomator:
    def __init__(self, mytext, email, password):
        """Initialize the GoogleFormAutomator class"""
        self.mytext = mytext
        self.email = email
        self.password = password
        self.driver = CustomChrome()
        self.driver.delete_all_cookies()

    def login(self):
        """Login to Google account and handle any security checks"""
        self.driver.get('https://accounts.google.com/ServiceLogin')
        
        try:
            email_input = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="identifierId"]'))
            )
            email_input.send_keys(self.email)
            next_button = self.driver.find_element(By.XPATH, '//*[@id="identifierNext"]/div/button/span')
            next_button.click()
            password_input = WebDriverWait(self.driver, 50).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input'))
            )
            password_input.send_keys(self.password)
            next_button = self.driver.find_element(By.XPATH, '//*[@id="passwordNext"]/div/button/span')
            next_button.click()

            WebDriverWait(self.driver, 30).until(
                EC.url_changes('https://accounts.google.com/ServiceLogin')
            )
            logger.info("Login successful.")
            
        except Exception as e:
            logger.error(f"Error during login: {e}")

    def wait_for_page_load(self):
        """Wait for the page to load completely by waiting for the body tag"""
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        logger.info("Page fully loaded.")

    def fill_form(self):
        """Navigate to the Google Form and fill it out"""
        self.driver.get('https://docs.google.com/forms/d/e/1FAIpQLSeUYMkI5ce18RL2aF5C8I7mPxF7haH23VEVz7PQrvz0Do0NrQ/viewform')
        self.wait_for_page_load()
        try:
            try:
                send_result = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[2]/div[3]/div[2]/span'))
            )
                click_next = self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div[3]/div[2]/span')
                click_next.click()
            except Exception as e:
                logger.info(f"Error during form submission: {e}")
            
            send_result = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div[2]/textarea'))
            )
            sleep(2)
            send_result.clear() 
            send_result.send_keys(self.mytext)

            email_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div[1]/label/div/div[2]/div/span'))
            )
            email_button.click()

            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div/span/span'))
            )
            submit_button.click()
            logger.info("Form successfully submitted.")
        
        except NoSuchWindowException:
            logger.warning("The browser window was closed before the form could be submitted.")

    def close_browser(self):
        """Close the browser after form submission"""
        try:
            self.driver.quit()
            logger.info("Browser closed.")
        except NoSuchWindowException:
            logger.warning("Browser window was already closed.")

