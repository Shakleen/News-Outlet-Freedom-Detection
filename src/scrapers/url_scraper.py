import random
import time
import os
import pandas as pd

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class URLScraper:
    def __init__(self, wait_time: int = 30, total: int = 1e4,
                 pause_min: int = 5, pause_max: int = 25):
        options = webdriver.ChromeOptions()
        options.binary_location = r"D:\Studying\UoR\1. Data Mining\Final_Project\chromedriver.exe"
        self.driver = webdriver.Chrome(keep_alive=True, options=options)
        self.wait_time = wait_time
        self.save_file_path = os.path.join("data", "reuters_url.csv")
        self.saved = 0
        self.total = total
        self.pause_min = pause_min
        self.pause_max = pause_max
        
    def get_urls(self):
        self._load_website()
        self._wait_until_search_list_visible()
        
        # while self.saved < self.total:
        self._save_info()
            # time.sleep(random.randint(self.pause_min, self.pause_max))
        self._click_load_more_button()
            

    def _click_load_more_button(self):
        try:
            load_more_button = self.driver.find_element(By.CLASS_NAME, "search-result-more-txt")
            
            # pos_y = load_more_button.rect['y']
            
            ActionChains(self.driver).move_to_element(load_more_button).perform()
            command = "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});"
            self.driver.execute_script(command, load_more_button)
            load_more_button.click()
        except NoSuchElementException:
            print("Load more button not found!")

    def _save_info(self):
        info_dict = {"link": [], "title": [], "timestamp": []}
        search_result_list_e = self.driver.find_element(By.CLASS_NAME, "search-result-list")
        content_list = search_result_list_e.find_elements(By.CLASS_NAME, "search-result-content")
        
        for content in content_list[self.saved:]:
            link, title = self._get_link_and_text(content)
            timestamp = self._get_timestamp(content)
            
            info_dict["link"].append(link)
            info_dict["title"].append(title)
            info_dict["timestamp"].append(timestamp)
            
        pd.DataFrame.from_dict(info_dict)\
            .to_csv(self.save_file_path, header=not os.path.exists(self.save_file_path),
                    mode="a", index=False)
        self.saved += len(content_list)
        print(f"Total saved so far: {self.saved}")

    def _get_timestamp(self, content):
        timestamp = ""
        
        try:
            element = content.find_element(By.CLASS_NAME, "search-result-timestamp")
            timestamp = element.text
        except NoSuchElementException:
            pass
        
        return timestamp

    def _get_link_and_text(self, content):
        link, title = "", ""
        
        try:
            title = content.find_element(By.CLASS_NAME, "search-result-title")
            a = title.find_element(By.TAG_NAME, "a")
            link = a.get_attribute("href")
            title = a.text
        except NoSuchElementException:
            pass
        
        return link, title

    def _load_website(self):
        # TODO: Make the search term a parameter
        base_url = 'https://www.reuters.com/search/news?blob=china&sortBy=relevance&dateRange=all'
        self.driver.get(base_url)

    def _wait_until_search_list_visible(self):
        wait = WebDriverWait(self.driver, timeout=self.wait_time)
        wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "search-result-list")),
            message="Timed out. Couldn't find search result.")
        
    def finish(self):
        self.driver.quit()