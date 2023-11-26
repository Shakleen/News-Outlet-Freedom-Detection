from typing import List
import re
import os
import pandas as pd

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
        self.process()
        self.save()
        
    def process(self):
        raise NotImplementedError
        
    def save(self):
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
        
if __name__ == "__main__":
    file_path = r"D:\Studying\UoR\1. Data Mining\Final_Project\data\reuters_canada.csv"
    save_path = r"D:\Studying\UoR\1. Data Mining\Final_Project\data\cleaned"
    cleaner = BaseCleaner(file_path, save_path)