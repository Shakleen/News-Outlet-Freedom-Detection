import random
import time
import os

from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_scraper import BaseScraper

class ReutersScraper(BaseScraper):
    def __init__(self, 
                 search_term: str,
                 wait_time: int = 30, total: int = 1e5,
                 pause_min: int = 1, pause_max: int = 10):
        super().__init__(wait_time, total, pause_min, pause_max)
        self.search_term = search_term
        self.save_file_path = os.path.join("data", f"reuters_{self.search_term}.csv")
        self._populate_unique_links()

    def _click_load_more_button(self):
        try:
            load_more_button = self.driver.find_element(By.CLASS_NAME, "search-result-more-txt")
            ActionChains(self.driver).scroll_to_element(load_more_button).perform()
            load_more_button.click()
        except NoSuchElementException:
            print("Load more button not found!")
            raise NoSuchElementException

    def _save_info(self):
        search_result_list_e = self.driver.find_element(By.CLASS_NAME, "search-result-list")
        content_list = search_result_list_e.find_elements(By.CLASS_NAME, "search-result-content")
        
        links = self._get_links(content_list)
        self._scrap_data_from_links(links)
        
        time.sleep(random.randint(self.pause_min, self.pause_max))
        self._print_elapsed_time()
    
    def _get_links(self, content_list):
        links = []
        
        for content in content_list[self.saved:]:
            link = self._get_link(content)
            
            if link is not None or link not in self.unique_links:
                links.append(link)
                
        return links

    def _get_link(self, content):
        link = ""
        
        try:
            title = content.find_element(By.CLASS_NAME, "search-result-title")
            a = title.find_element(By.TAG_NAME, "a")
            link = a.get_attribute("href")
        except NoSuchElementException:
            pass
        
        return link

    def _load_website(self):
        base_url = f'https://www.reuters.com/search/news?blob={self.search_term}&sortBy=relevance&dateRange=all'
        self.driver.get(base_url)

    def _wait_until_search_list_visible(self):
        wait = WebDriverWait(self.driver, timeout=self.wait_time)
        wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "search-result-list")),
            message="Timed out. Couldn't find search result.")
    