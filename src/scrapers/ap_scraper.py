import os
import time
import random

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

from .base_scraper import BaseScraper

class APScraper(BaseScraper):
    def __init__(self, 
                 search_term: str = "", 
                 wait_time: int = 30, 
                 total: int = 100000, 
                 pause_min: int = 1, 
                 pause_max: int = 10):
        super().__init__(wait_time, total, pause_min, pause_max)
        self.search_term = search_term
        self.save_file_path = os.path.join("data", f"ap_{search_term}.csv")
        self._populate_unique_links()
    
    def _load_website(self):
        base_url = f'https://apnews.com/search?q={self.search_term}&f2=00000188-f942-d221-a78c-f9570e360000&s=0'
        self.driver.get(base_url)
        
    def _wait_until_search_list_visible(self):
        wait = WebDriverWait(self.driver, timeout=self.wait_time)
        wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "SearchResultsModule-results")),
            message="Timed out. Couldn't find \"PageList-items\".")
        
    def _save_info(self):
        content_list = self.driver.find_element(By.CLASS_NAME, "SearchResultsModule-results")
        elements = content_list.find_elements(By.CLASS_NAME, "PagePromo-title")
        links = self._get_links(elements)
        self._scrap_data_from_links(links)
        
        time.sleep(random.randint(self.pause_min, self.pause_max))
        self._print_elapsed_time()
        
    def _get_links(self, elements):
        links = []
        
        for element in elements:
            a = element.find_element(By.TAG_NAME, "a")
            link = a.get_attribute("href")
            
            if link is not None or link not in self.unique_links:
                links.append(link)
                
        return links
    
    def _click_load_more_button(self):
        try:
            div = self.driver.find_element(By.CLASS_NAME, "Pagination-nextPage")
            next_button = div.find_element(By.TAG_NAME, "a")
            ActionChains(self.driver).scroll_to_element(next_button).perform()
            next_button.click()
        except NoSuchElementException:
            print("Next button not found!")
            raise NoSuchElementException