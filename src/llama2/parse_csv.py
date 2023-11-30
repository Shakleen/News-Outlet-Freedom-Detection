import re
import pandas as pd


class ParseCSV:
    def __call__(self, file_path: str):
        df = pd.read_csv(file_path)
        
        df["sentiment_class"] = df.answer.map(
            lambda x: self.get_category(x, "Sentiment:.+\n"))
        df["stance_class"] = df.answer.map(
            lambda x: self.get_category(x, "Stance:.+\n"))
        
        df["sentiment_score"] = df.answer.map(
            lambda x: self.get_score(x, 0))
        df["stance_score"] = df.answer.map(
            lambda x: self.get_score(x, 1))
        
        df["sentiment_reason"] = df.answer.map(
            lambda x: self.get_reason(x, 0))
        df["stance_reason"] = df.answer.map(
            lambda x: self.get_reason(x, 1))
        
        return df
        
    def get_reason(self, text, id):
        pattern = "(?<=Reason:).+"
        matches = [match for match in re.finditer(pattern, text)]
        
        if matches is None:
            return None
        
        return text[matches[id].start() : matches[id].end()].strip()
    
    def get_category(self, text, pattern):
        match = re.search(pattern, text)
        
        if match is None:
            return None
        
        return text[match.start():match.end()].split()[-1].lower()
    
    def get_score(self, text, id):
        pattern = "Score:.+\n"
        matches = [match for match in re.finditer(pattern, text)]
        
        if matches is None:
            return None
        
        return float(text[matches[id].start() : matches[id].end()].split()[-1])