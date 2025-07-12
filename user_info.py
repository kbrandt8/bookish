import csv

class UserInfo:
    def __init__(self):
        self.bookshelf = []
        self.all_books = []

    def story_graph_csv(self,file):
        with open (file,'r',encoding='utf-8',errors='ignore') as f:
            reader = csv.DictReader(f)
            self.bookshelf += [
                {
                    "Title":row['Title'],
                    "Author": row['Authors'],
                    "Rating":row['Star Rating'],

                }
                for row in reader
                ]

            self.sort_shelf()

    def good_reads_csv(self,file):
        with open (file,'r',encoding='utf-8',errors='ignore') as f:
            reader = csv.DictReader(f)
            self.bookshelf += [
                {
                    "Title":row['Title'],
                    "Author":row['Author'],
                    "Rating":row['My Rating']
                }
                for row in reader
                ]

            self.sort_shelf()

    def sort_shelf(self):
        self.all_books = [book for id, book in enumerate(self.bookshelf) if book not in self.bookshelf[id+1:]]


