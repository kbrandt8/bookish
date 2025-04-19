from bs4.diagnose import rword

from utils import make_soup
import csv


class StoryGraph():
    def __init__(self, file=str):
        self.file = file
        self.bookshelf = []
        self.get_csv()

    def get_csv(self):
        with open (self.file,'r',encoding='utf-8',errors='ignore') as f:
            reader = csv.DictReader(f)
            self.bookshelf = [
                {
                    "Title":row['Title'],
                    "ISBN":row['ISBN/UID'],
                    "Author":row['Authors'],
                }
                for row in reader
                if row['Star Rating'] and row['ISBN/UID'] and float(row['Star Rating']) >= 4]


