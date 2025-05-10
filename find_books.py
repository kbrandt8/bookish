import csv
import requests
class FindBooks:
    def __init__(self,file):
        self.file = file
        self.book_recommendations = []

    def get_shelf(self):
        with open(self.file,'r',encoding='utf-8',errors='ignore') as f:
            reader = csv.DictReader(f)
            self.book_recommendations += [
                {
                    "Title": row['title'],
                    "Author":row['author_name']
                 }
                for row in reader
            ]
    def get_book(self,book):
        url=f"https://www.googleapis.com/books/v1/volumes?q=inauthor:{book['Author']},intitle:{book['Title']}&filter=ebooks&langRestrict=en"
        result = requests.get(url)
        books = result.json()
        for book in books:

