from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


class Scrapper:

    def get_url_sale(self):
        pass

    def set_up(self):
        self.start_url = "https://www.immoweb.be/en"
        self.buy = "#homepage-tab-buy"

        self.driver = webdriver.Chrome()
        self.driver.get(self.start_url)

        self.cookie_button = self.driver.find_element(
            By.XPATH, " //button[@data-testid='uc-accept-all-button']"
        )
        self.cookie_button.click()

        # self.search_button = self.driver.find_element(
        #     By.XPATH, "//button[@id='searchBoxSubmitButton']"
        # )
        # self.url = self.driver.current_url
        # self.driver.close()
