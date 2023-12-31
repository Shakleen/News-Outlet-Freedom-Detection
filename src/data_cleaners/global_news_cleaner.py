import re
import numpy as np

from .base_cleaner import BaseCleaner

class GlobalNewsCleaner(BaseCleaner):
    def process(self):
        self.process_text()
        self.process_rows()

    def process_text(self):
        funcs = [self.remove_emails,
                 self.discard_initial_share_sentence,
                 self.remove_links,
                 self.discard_postfix_editorial,
                 self.discard_initial_share_sentences,
                 self.discard_story_continues,
                 self.discard_writers_section,
                 lambda x: re.sub(r"UPDATE \| ", "", x),
                 lambda x: re.sub(r'\s+', ' ', x).strip()]
        
        print("Started text processing")
        
        for func in funcs:
            self.data.maintext = self.data.maintext.apply(func)
            print(f"{func.__name__} done")
        
        print("finished text processing")
    
    def discard_initial_share_sentence(self, text):
        position = self.find_first_instance(text, "Send this page to someone .+\n")
        
        if position is None:
            return text
        
        return text[:position[0]] + text[position[1]:]
    
    def discard_initial_share_sentences(self, text):
        position = self.find_first_instance(text, "Share this item on Facebook\n")
        
        if position is None:
            return text
        
        return text[position[1]:]
    
    def discard_writers_section(self, text):
        position = self.find_last_instance(text, "(—|— )?Associated Press writers.+")
        
        if position is None:
            return text
        
        return text[:position[0]]
    
    def discard_story_continues(self, text):
        return re.sub("Story continues below advertisement\n", "", text)
    
    def discard_postfix_editorial(self, text):
        pattern = "(—)? With files from (.+)?"
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