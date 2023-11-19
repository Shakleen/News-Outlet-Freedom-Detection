import pandas as pd
import os
import time
from collections import defaultdict

from newsplease import NewsPlease
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class BaseScraper:
    def __init__(self, 
                 wait_time: int = 30, 
                 total: int = 1e5,
                 pause_min: int = 1, 
                 pause_max: int = 10):
        options = webdriver.ChromeOptions()
        options.binary_location = r"D:\Studying\UoR\1. Data Mining\Final_Project\chromedriver.exe"
        self.driver = webdriver.Chrome(keep_alive=True, options=options)
        self.wait_time = wait_time
        self.saved = 0
        self.total = total
        self.pause_min = pause_min
        self.pause_max = pause_max
        self.start = time.time()
        self.unique_links = set()
        
    def _populate_unique_links(self):
        if os.path.exists(self.save_file_path):
            df = pd.read_csv(self.save_file_path)
            self.unique_links = set(df.url.to_list())
            del df
            
    def get_urls(self):
        self._load_website()
        self._wait_until_search_list_visible()
        
        while self.saved < self.total:
            self._save_info()
            self._click_load_more_button()
            
    def _click_load_more_button(self):
        raise NotImplementedError
    
    def _save_info(self):
        raise NotImplementedError
    
    def _print_elapsed_time(self):
        elapsed = (time.time() - self.start)
        s = int(elapsed % 60)
        m = int(((elapsed - s) // 60) % 60)
        h = int((elapsed - m * 60 - s) // 3600)
        print(f"[{h:02}h {m:02}m {s:02}s] Total saved so far: {self.saved}")

    def _get_links(self, elements):
        raise NotImplementedError
    
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
        del dict
        
    def _get_link(self, content):
        raise NotImplementedError
    
    def _load_website(self):
        raise NotImplementedError
    
    def _wait_until_search_list_visible(self):
        raise NotImplementedError
        
    def finish(self):
        self.driver.quit()