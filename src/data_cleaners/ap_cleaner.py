import re
import numpy as np

from .base_cleaner import BaseCleaner

class APCleaner(BaseCleaner):
    def process(self):
        self.process_text()
        self.process_rows()

    def process_text(self):
        funcs = [self.remove_links,
                 self.discard_initial_location_and_date,
                 self.discard_postfix_refs,
                 self.discard_photo_by,
                 self.discard_postfix_editorial,
                 self.discard_postfix_reported_from,
                 self.discard_postfix_socials,
                 self.discard_postfix_credits,
                 lambda x: re.sub("\n(_{2,}|—-?)\n", "\n", x),
                 lambda x: re.sub(r'\s+', ' ', x).strip()]
        
        print("Started text processing")
        
        for func in funcs:
            self.data.maintext = self.data.maintext.apply(func)
            print(f"{func.__name__} done")
        
        print("finished text processing")
    
    def discard_initial_location_and_date(self, text):
        position = self.find_first_instance(text, "\(AP\) (-|—) ")
        
        if position is None:
            return text
        
        return text[position[1]:]
    
    def discard_postfix_refs(self, text):
        position = self.find_first_instance(text, "AP .+?:")
        
        if position is None:
            return text
        
        return text[:position[0]]
    
    def discard_photo_by(self, text):
        return re.sub(r"\(AP Photo/.+?\)", "", text)
    
    def discard_postfix_editorial(self, text):
        position = self.find_first_instance(text, "Associated Press writer")
        
        if position is None:
            return text
        
        return text[:position[0]]
    
    def discard_postfix_reported_from(self, text):
        position = self.find_first_instance(text, ".+? reported from")
        
        if position is None:
            return text
        
        return text[:position[0]]
    
    def discard_postfix_socials(self, text):
        position = self.find_first_instance(text, ".+? is at https")
        
        if position is None:
            return text
        
        return text[:position[0]]
    
    def discard_postfix_credits(self, text):
        position = self.find_first_instance(text, "Associated Press religion coverage")
        
        if position is None:
            return text
        
        return text[:position[0]]

    def process_rows(self):
        funcs = [self.drop_zero_lengths,
                 self.drop_unrelated_geo_news,
                 self.drop_short_news]
        
        print("Started row processing")
        
        for func in funcs:
            func()
            print(f"{func.__name__} done")
            print(f"Data shape: {self.data.shape}")
        
        print("Finished row processing")
    
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
    
    
class APCanada(APCleaner):
    def drop_unrelated_geo_news(self):
        frequent_words = ["Canada", "Alberta", "Montreal", "Toronto", 
                          "British Columbia", "Saskatchewan", "Quebec", 
                          "Ontario", "Manitoba", "Newfoundland", "Yukon", 
                          "Canadian"]
        temp = self.data.maintext.apply(
            lambda x: self.includes_words(x, frequent_words))
        self.data.drop(self.data[~temp].index, inplace=True)
        
        
class APChina(APCleaner):
    def drop_unrelated_geo_news(self):
        frequent_words = ["China", "Chinese", "Beijing", "Xi"]
        
        temp = self.data.maintext.apply(
            lambda x: self.includes_words(x, frequent_words))
        self.data.drop(self.data[~temp].index, inplace=True)
        
        
class APRussia(APCleaner):
    def drop_unrelated_geo_news(self):
        frequent_words = ["Russia", "Russian", "Moscow", "Putin"]
        
        temp = self.data.maintext.apply(
            lambda x: self.includes_words(x, frequent_words))
        self.data.drop(self.data[~temp].index, inplace=True)