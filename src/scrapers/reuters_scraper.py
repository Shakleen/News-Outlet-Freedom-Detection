import random
import time
import os
import pandas as pd
from newsplease import NewsPlease
from collections import defaultdict

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class ReutersScraper:
    def __init__(self, 
                 search_term: str,
                 wait_time: int = 30, total: int = 1e5,
                 pause_min: int = 1, pause_max: int = 10):
        options = webdriver.ChromeOptions()
        options.binary_location = r"D:\Studying\UoR\1. Data Mining\Final_Project\chromedriver.exe"
        self.driver = webdriver.Chrome(keep_alive=True, options=options)
        self.wait_time = wait_time
        self.save_file_path = os.path.join("data", f"reuters_{search_term}.csv")
        self.saved = 0
        self.total = total
        self.pause_min = pause_min
        self.pause_max = pause_max
        self.start = time.time()
        self.search_term = search_term
        self.unique_links = set()
        
        if os.path.exists(self.save_file_path):
            df = pd.read_csv(self.save_file_path)
            self.unique_links = set(df.url.to_list())
        
    def get_urls(self):
        self._load_website()
        self._wait_until_search_list_visible()
        
        while self.saved < self.total:
            self._save_info()
            self._click_load_more_button()

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
        
        elapsed_minutes = (time.time() - self.start) / 60
        print(f"[{elapsed_minutes:>10.2f}m] Total saved so far: {self.saved}")

    def _get_links(self, content_list):
        links = []
        
        for content in content_list[self.saved:]:
            link = self._get_link(content)
            
            if link is not None or link not in self.unique_links:
                links.append(link)
                
        return links

    def _scrap_data_from_links(self, links):
        try:
            article = NewsPlease.from_urls(links, self.wait_time)
            self._save_articles(article)
        except Exception:
            pass

    def _save_articles(self, article):
        dict = defaultdict(list)
            
        for data in article.values():
            for key, value in data.get_dict().items():
                dict[key].append(value)
                
        self.unique_links |= set(dict["url"])
        self.saved = len(self.unique_links)
            
        pd.DataFrame.from_dict(dict).to_csv(
                self.save_file_path, 
                header=not os.path.exists(self.save_file_path),
                mode="a", index=False)

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
        
    def finish(self):
        self.driver.quit()