import os
import time
import random

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

from .reuters_scraper import ReutersScraper

class CBCScraper(ReutersScraper):
    def __init__(self, 
                 search_term: str = "", 
                 wait_time: int = 30, 
                 total: int = 100000, 
                 pause_min: int = 1, 
                 pause_max: int = 10):
        super().__init__(search_term, wait_time, total, pause_min, pause_max)
        self.save_file_path = os.path.join("data", f"cbc.csv")
    
    def _load_website(self):
        base_url = 'https://www.cbc.ca/search?q=canada&section=news&sortOrder=relevance&media=all'
        self.driver.get(base_url)
        
    def _wait_until_search_list_visible(self):
        wait = WebDriverWait(self.driver, timeout=self.wait_time)
        wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "contentListCards")),
            message="Timed out. Couldn't find \"Content List Cards\".")
        
    def _save_info(self):
        content_list = self.driver.find_element(By.CLASS_NAME, "contentListCards")
        elements = content_list.find_elements(By.CLASS_NAME, "cardListing")
        links = self._get_links(elements)
        self._scrap_data_from_links(links)
        
        time.sleep(random.randint(self.pause_min, self.pause_max))
        
        elapsed_minutes = (time.time() - self.start) / 60
        print(f"[{elapsed_minutes:>10.2f}m] Total saved so far: {self.saved}")
        
    def _get_links(self, elements):
        links = []
        
        for a in elements[self.saved:]:
            link = a.get_attribute("href")
            
            if link is not None or link not in self.unique_links:
                links.append(link)
                
        return links
    
    def _click_load_more_button(self):
        try:
            notice_button = self.driver.find_element(By.CLASS_NAME, "noticeButton")
            notice_button.click()
        except NoSuchElementException:
            pass
        
        try:
            load_more_button = self.driver.find_element(By.CLASS_NAME, "loadMore")
            ActionChains(self.driver).scroll_to_element(load_more_button).perform()
            load_more_button.click()
            time.sleep(10)
        except NoSuchElementException:
            print("Load more button not found!")
            raise NoSuchElementException