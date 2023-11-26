import numpy as np

from .base_cleaner import BaseCleaner

class MoscowTimesCleaner(BaseCleaner):
    def process(self):
        self.data.maintext = self.data.maintext.apply(self.remove_links)
        self.drop_zero_lengths()
        self.drop_unrelated_geo_news()
        self.drop_short_news()
    
    def drop_zero_lengths(self):
        temp = self.data.loc[:, ["maintext", "title"]]\
            .apply(lambda row: [len(col) for col in row])
        temp.apply(lambda row: [col == 0 for col in row]).sum()
        cond = (temp.title <= 0) | (temp.maintext <= 0)
        self.data.drop(temp[cond].index, inplace=True)
        
    def drop_unrelated_geo_news(self):
        frequent_words = ["Russia", "Russian", "Moscow", "Putin"]
        
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