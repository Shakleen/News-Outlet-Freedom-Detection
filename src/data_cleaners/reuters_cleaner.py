import re
import numpy as np

from .base_cleaner import BaseCleaner

class ReutersCleaner(BaseCleaner):
    def process(self):
        self.process_text()
        self.process_rows()

    def process_text(self):
        funcs = [self.discard_reporting_by,
                 self.remove_links,
                 self.remove_read_more,
                 self.discard_initial_location_and_date,
                 self.discard_initial_breaking_news,
                 lambda x: re.sub(r'\s+', ' ', x).strip()]
        
        print("Started text processing")
        
        for func in funcs:
            self.data.maintext = self.data.maintext.apply(func)
            print(f"{func.__name__} done")
        
        print("finished text processing")
        
    def discard_reporting_by(self, text):
        position = self.find_last_instance(text, "Reporting by")
        
        if position is None:
            return text
        
        return text[:position[0]]
        
    def remove_read_more(self, text):
        return re.sub("STORIES: read more\n", "", text)
    
    def discard_initial_location_and_date(self, text):
        position = self.find_first_instance(text, "\(Reuters\) - ")
        
        if position is None:
            return text
        
        return text[position[1]:]
    
    def discard_initial_breaking_news(self, text):
        position = self.find_first_instance(text, "\(Reuters Breakingviews\) - ")
        
        if position is None:
            return text
        
        return text[position[1]:]

    def process_rows(self):
        funcs = [self.drop_annual_inflation_rate_news,
                 self.drop_zero_lengths,
                 self.drop_unrelated_geo_news,
                 self.drop_short_news]
        
        print("Started row processing")
        
        for func in funcs:
            func()
            print(f"{func.__name__} done")
            print(f"Data shape: {self.data.shape}")
        
        print("Finished row processing")
    
    def drop_annual_inflation_rate_news(self):
        temp = self.data.title.apply(
            lambda x: x.find("annual inflation rate") != -1)
        self.data.drop(self.data[temp].index, inplace=True)
    
    def drop_zero_lengths(self):
        temp = self.data.loc[:, ["maintext", "title"]]\
            .apply(lambda row: [len(col) for col in row])
        temp.apply(lambda row: [col == 0 for col in row]).sum()
        cond = (temp.title <= 0) | (temp.maintext <= 0)
        self.data.drop(temp[cond].index, inplace=True)
    
    def drop_unrelated_geo_news(self):
        raise NotImplementedError
        
    def includes_words(self, text, frequent_words):
        for word in frequent_words:
            if word in text.split():
                return True
            
        return False
    
    
class ReutersCanada(ReutersCleaner):
    def drop_unrelated_geo_news(self):
        frequent_words = ["Canada", "Alberta", "Montreal", "Toronto", 
                          "British Columbia", "Saskatchewan", "Quebec", 
                          "Ontario", "Manitoba", "Newfoundland", "Yukon", 
                          "Canadian"]
        temp = self.data.maintext.apply(
            lambda x: self.includes_words(x, frequent_words))
        self.data.drop(self.data[~temp].index, inplace=True)
        
        
class ReutersChina(ReutersCleaner):
    def drop_unrelated_geo_news(self):
        frequent_words = ["China", "Chinese", "Beijing", "Xi"]
        
        temp = self.data.maintext.apply(
            lambda x: self.includes_words(x, frequent_words))
        self.data.drop(self.data[~temp].index, inplace=True)
        
        
class ReutersRussia(ReutersCleaner):
    def drop_unrelated_geo_news(self):
        frequent_words = ["Russia", "Russian", "Moscow", "Putin"]
        
        temp = self.data.maintext.apply(
            lambda x: self.includes_words(x, frequent_words))
        self.data.drop(self.data[~temp].index, inplace=True)