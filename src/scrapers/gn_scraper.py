import os
import time
import random

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import NoSuchElementException
from selenium.common import MoveTargetOutOfBoundsException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

from .base_scraper import BaseScraper

class GNScraper(BaseScraper):
    def __init__(self,  
                 wait_time: int = 30, 
                 total: int = 100000, 
                 pause_min: int = 1, 
                 pause_max: int = 10):
        super().__init__(wait_time, total, pause_min, pause_max)
        self.save_file_path = os.path.join("data", "global-news.csv")
        self._populate_unique_links()
    
    def _load_website(self):
        base_url = 'https://globalnews.ca/?s=canada'
        self.driver.get(base_url)
        
    def _wait_until_search_list_visible(self):
        wait = WebDriverWait(self.driver, timeout=self.wait_time)
        wait.until(EC.visibility_of_element_located(
            (By.ID, "search-results-wrapper-es")),
            message="Timed out. Couldn't find \"Content List Cards\".")
        
    def _save_info(self):
        content_list = self.driver.find_element(By.ID, "search-results-wrapper-es")
        elements = content_list.find_elements(By.TAG_NAME, "a")
        links = self._get_links(elements)
        self._scrap_data_from_links(links)
        
        time.sleep(random.randint(self.pause_min, self.pause_max))
        self._print_elapsed_time()
        
    def _get_links(self, elements):
        links = []
        
        for a in elements[self.saved:]:
            link = a.get_attribute("href")
            
            if link is not None or link not in self.unique_links:
                links.append(link)
                
        return links
    
    def _click_load_more_button(self):
        try:
            notice_button = self.driver.find_element(By.ID, "_evidon-accept-button")
            notice_button.click()
        except NoSuchElementException:
            pass
        
        for _ in range(5):
            try:
                load_more_button = self.driver.find_element(By.ID, "load-more-results")
                ActionChains(self.driver).scroll_to_element(load_more_button).perform()
                load_more_button.click()
                time.sleep(random.randint(self.pause_min, self.pause_max))
                break
            except NoSuchElementException:
                print("Load more button not found!")
            except MoveTargetOutOfBoundsException:
                print("Load More button moved.")
            
            time.sleep(random.randint(3, 5))