import re
import numpy as np

from .base_cleaner import BaseCleaner

class CBCCleaner(BaseCleaner):
    def process(self):
        self.process_text()
        self.process_rows()

    def process_text(self):
        funcs = [self.remove_emails,
                 self.discard_photo_by,
                 self.remove_links,
                 self.discard_warning_text,
                 lambda x: re.sub(r"UPDATE \| ", "", x),
                 lambda x: re.sub(r'\s+', ' ', x).strip()]
        
        print("Started text processing")
        
        for func in funcs:
            self.data.maintext = self.data.maintext.apply(func)
            print(f"{func.__name__} done")
        
        print("finished text processing")
    
    def discard_photo_by(self, text):
        pattern = r'\(Photo .+?\)'
        return re.sub(pattern, '', text)
    
    def discard_warning_text(self, text):
        pattern = "WARNING: This story contains distressing details."
        return re.sub(pattern, "", text)

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
        frequent_words = ["Canada", "Alberta", "Montreal", "Toronto", 
                          "British Columbia", "Saskatchewan", "Quebec", 
                          "Ontario", "Manitoba", "Newfoundland", "Yukon", 
                          "Canadian"]
        temp = self.data.maintext.apply(
            lambda x: self.includes_words(x, frequent_words))
        self.data.drop(self.data[~temp].index, inplace=True)
        
    def includes_words(self, text, frequent_words):
        for word in frequent_words:
            if word in text.split():
                return True
            
        return False
    
    def drop_short_news(self):
        temp = self.data.loc[:, ["maintext", "title"]]\
            .apply(lambda row: [len(col.split()) for col in row])
        main_to_drop = self.low_outliers(temp.maintext)
        title_to_drop = self.low_outliers(temp.title)
        cond = main_to_drop | title_to_drop
        self.data.drop(temp[cond].index, inplace=True)
            
    def low_outliers(self, temp):
        q1 = np.quantile(temp, 0.25)
        q3 = np.quantile(temp, 0.75)
        iqr = q3 - q1
        span = 1.5 * iqr
        low = np.floor(q1 - span)
        return (temp < low)