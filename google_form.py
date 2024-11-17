from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from time import sleep

class CustomChrome(uc.Chrome):
    def __del__(self):
        pass  

class GoogleFormAutomator:
    def __init__(self, mytext):
        self.driver = CustomChrome()
        self.mytext = mytext
        self.driver.delete_all_cookies()

    def login(self):
        self.driver.get('https://accounts.google.com/ServiceLogin')
        sleep(60)  # TODO: replace with a more robust wait method if needed

    def fill_form(self):
        self.driver.get('https://docs.google.com/forms/d/e/1FAIpQLSeUYMkI5ce18RL2aF5C8I7mPxF7haH23VEVz7PQrvz0Do0NrQ/viewform')
        sleep(2)

        send_result = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div[2]/textarea'))
        )
        send_result.clear()
        send_result.send_keys(self.mytext)
        sleep(2)

        email_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div[1]/label/div/div[2]/div/span'))
        )
        email_button.click()
        sleep(2)

        submit_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div/span/span'))
        )
        submit_button.click()
        sleep(1.5)


# Usage:
mytext = "{'strat_7': -0.03779352948676801, 'strat_8': -0.03779352948676801, ... , 'team_name': 'Longer Term Capital Management', 'passcode': 'DogCat'}"
google_form = GoogleFormAutomator(mytext)
google_form.login()
google_form.fill_form()
