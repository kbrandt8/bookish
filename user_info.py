import csv
import re

class UserInfo():
    def __init__(self):
        self.bookshelf = []

    def story_graph_csv(self,file):
        with open (file,'r',encoding='utf-8',errors='ignore') as f:
            reader = csv.DictReader(f)
            self.bookshelf += [
                {
                    "Title":row['Title'],
                    "ISBN":row['ISBN/UID'],
                    "Author":row['Authors'],
                }
                for row in reader
                if row['Star Rating'] and row['ISBN/UID'] and float(row['Star Rating']) >= 4]
            self.sort_shelf()

    def good_reads_csv(self,file):
        with open (file,'r',encoding='utf-8',errors='ignore') as f:
            reader = csv.DictReader(f)
            self.bookshelf += [
                {
                    "Title":row['Title'],
                    "ISBN":re.search(r'\d+',row['ISBN13']).group(),
                    "Author":row['Author'],
                }
                for row in reader
                if row['My Rating'] and row['ISBN'] and row['ISBN'] !='=""' and float(row['My Rating']) >= 4]
            self.sort_shelf()

    def sort_shelf(self):
        self.bookshelf = [book for id,book in enumerate(self.bookshelf) if book not in self.bookshelf[id+1:]]

