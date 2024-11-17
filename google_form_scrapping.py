from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from time import sleep

class CustomChrome(uc.Chrome):
    def __del__(self):
        """Override destructor if needed to ensure proper cleanup"""
        pass  

class GoogleFormAutomator:
    def __init__(self, mytext):
        """Initialize the GoogleFormAutomator class"""
        self.driver = CustomChrome()
        self.mytext = mytext
        self.driver.delete_all_cookies()

    def login(self):
        """Login to Google account and handle any security checks"""
        self.driver.get('https://accounts.google.com/ServiceLogin')
        
        try:
            # Wait until email input field is visible
            email_input = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="identifierId"]'))
            )
            email_input.send_keys("imperialalgothon@gmail.com")
            next_button = self.driver.find_element(By.XPATH, '//*[@id="identifierNext"]/div/button/span')
            next_button.click()

            # Wait until password field is visible
            password_input = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input'))
            )
            password_input.send_keys("DogCat@123")
            next_button = self.driver.find_element(By.XPATH, '//*[@id="passwordNext"]/div/button/span')
            next_button.click()

            # Optional: Handle potential two-step verification or other prompts if they appear
            WebDriverWait(self.driver, 30).until(
                EC.url_changes('https://accounts.google.com/ServiceLogin')
            )

            sleep(2)
            
        except Exception as e:
            print(f"Error during login: {e}")

    def fill_form(self):
        """Navigate to the Google Form and fill it out"""
        self.driver.get('https://docs.google.com/forms/d/e/1FAIpQLSeUYMkI5ce18RL2aF5C8I7mPxF7haH23VEVz7PQrvz0Do0NrQ/viewform')
        sleep(2)

        try:
            try:
                click_next = self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div[3]/div/span/span')
                click_next.click()
                sleep(1)
            except:
                # Wait for the textarea and input the predefined text
                send_result = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div[2]/textarea'))
                )
                send_result.clear()  # Clear any existing text
                send_result.send_keys(self.mytext)
                sleep(2)

                # Click the email checkbox
                email_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div[1]/label/div/div[2]/div/span'))
                )
                email_button.click()
                sleep(2)

                # Click the submit button
                submit_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div/span/span'))
                )
                submit_button.click()
                sleep(1.5)
        except Exception as e:
            print(f"Error during form submission: {e}")
