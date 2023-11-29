from typing import List
import re
import os
import pandas as pd
import numpy as np

class BaseCleaner:
    def __init__(self,
                 file_path: str,
                 save_path: str,
                 usecols: List[str] = None) -> None:
        assert os.path.exists(file_path), "File doesn't exist"
        self.data = pd.read_csv(file_path, usecols=usecols)
        self.save_path = save_path
        
        print(f"Loaded file: {file_path}")
        print(f"Data shape: {self.data.shape}")
        
    def __call__(self):
        self.impute()
        self.drop_duplicates()
        self.process()
        self.data.maintext = self.data.maintext.map(
            lambda x: re.sub(r'[^\x00-\x7F]+', '', x))
        self.save()
        
    def impute(self):
        self.data.fillna("", inplace=True)
        print(self.data.info())
        
    def process(self):
        raise NotImplementedError
        
    def save(self):
        print(self.data.info())
        self.data.to_csv(self.save_path, index=None)
        
    def get_matches(self, text, phrase):
        return [match for match in re.finditer(phrase, text)]
        
    def find_last_instance(self, text, phrase):
        matches = self.get_matches(text, phrase)
        
        if matches:
            last_match = matches[-1]
            return last_match.start(), last_match.end()
        
        return None
        
    def find_first_instance(self, text, phrase):
        matches = self.get_matches(text, phrase)
        
        if matches:
            first_match = matches[0]
            return first_match.start(), first_match.end()
        
        return None
        
    def remove_links(self, text):
        return re.sub(r'http\S+|www.\S+', '', text)
    
    def remove_emails(self, text):
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.sub(email_regex, '', text)
    
    def drop_duplicates(self):
        self.data.drop_duplicates(inplace=True, subset=['date_publish', 'title'])
    
    def drop_short_news(self):
        temp = self.data.loc[:, ["maintext", "title"]]\
            .apply(lambda row: [len(col.split()) for col in row])
        cond = self.outliers(temp.title)
        self.data.drop(temp[cond].index, inplace=True)
            
    def outliers(self, temp):
        q1 = np.quantile(temp, 0.25)
        q3 = np.quantile(temp, 0.75)
        iqr = q3 - q1
        span = 1.5 * iqr
        low = np.floor(q1 - span)
        high = np.ceil(q3 + span)
        return (temp <= low) | (temp >= high)
        
if __name__ == "__main__":
    file_path = r"D:\Studying\UoR\1. Data Mining\Final_Project\data\reuters_canada.csv"
    save_path = r"D:\Studying\UoR\1. Data Mining\Final_Project\data\cleaned"
    cleaner = BaseCleaner(file_path, save_path)