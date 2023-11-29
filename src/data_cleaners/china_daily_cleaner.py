import re
import numpy as np

from .base_cleaner import BaseCleaner

class ChinaDailyCleaner(BaseCleaner):
    def process(self):
        self.process_text()
        self.process_rows()

    def process_text(self):
        funcs = [self.remove_emails,
                 self.discard_china_daily_stamp,
                 self.discard_photo_by,
                 self.remove_links,
                 self.remove_read_more,
                 self.discard_initial_beijing,
                 self.discard_initial_reporter_name,
                 self.discard_initial_reporting_details,
                 lambda x: re.sub(r'\s+', ' ', x).strip()]
        
        print("Started text processing")
        
        for func in funcs:
            self.data.maintext = self.data.maintext.apply(func)
            print(f"{func.__name__} done")
        
        print("finished text processing")
        
    def remove_emails(self, text):
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.sub(email_regex, '', text)
        
    def discard_china_daily_stamp(self, text):
        position = self.find_last_instance(text, "\(China Daily")
        
        if position is None:
            return text
        
        return text[:position[0]]
    
    def discard_photo_by(self, text):
        pattern = r'\[Photo by .+?/.+?\]|\[Photo/.+?\]'
        return re.sub(pattern, '', text)
        
    def remove_read_more(self, text):
        return re.sub("STORIES: read more\n", "", text)
    
    def discard_initial_beijing(self, text):
        position = self.find_first_instance(text, "[A-Z]+ -+")
        
        if position is None:
            return text
        
        return text[:position[0]] + ' ' + text[position[1]:]
    
    def discard_initial_reporter_name(self, text):
        position = self.find_first_instance(text, ".+?/CHINA DAILY")
        
        if position is None:
            return text
        
        return text[position[1]:]
    
    def discard_initial_reporting_details(self, text):
        pattern = "Updated: (\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]) (0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])"
        position = self.find_first_instance(text, pattern)
        
        if position is None:
            return text
        
        return text[position[1]:]

    def process_rows(self):
        funcs = [self.drop_publish_media_online,
                 self.drop_zero_lengths,
                 self.drop_unrelated_geo_news,
                 self.drop_short_news]
        
        print("Started row processing")
        
        for func in funcs:
            func()
            print(f"{func.__name__} done")
            print(f"Data shape: {self.data.shape}")
        
        print("Finished row processing")
    
    def drop_publish_media_online(self):
        temp = self.data.maintext.apply(
            lambda x: x.find("License for publishing multimedia online") != -1)
        self.data.drop(self.data[temp].index, inplace=True)
    
    def drop_zero_lengths(self):
        temp = self.data.loc[:, ["maintext", "title"]]\
            .apply(lambda row: [len(col) for col in row])
        temp.apply(lambda row: [col == 0 for col in row]).sum()
        cond = (temp.title <= 0) | (temp.maintext <= 0)
        self.data.drop(temp[cond].index, inplace=True)
    
    def drop_unrelated_geo_news(self):
        frequent_words = ["China", "Chinese", "Beijing", "Shanghai", "Xi"]
        
        temp = self.data.maintext.apply(
            lambda x: self.includes_words(x, frequent_words))
        self.data.drop(self.data[~temp].index, inplace=True)
        
    def includes_words(self, text, frequent_words):
        for word in frequent_words:
            if word in text.split():
                return True
            
        return False