import csv
from typing import List, Dict

class UserInfo:
    def __init__(self):
        self.bookshelf: List[Dict[str, str]] = []
        self.all_books: List[Dict[str, str]] = []

    def load_csv(self,file_path, source:str):
        field_map = {
            "sg":{"title":"Title","author":"Authors","rating":"Star Rating" },
            "gr":{"title":"Title", "author":"Author","rating":"My Rating"}
        }
        if source not in field_map:
            raise ValueError(f"Unsupported source '{source}'")
        mapping = field_map[source]
        try:
            with open(file_path,'r',encoding='utf-8',errors='ignore') as f:
                reader = csv.DictReader(f)
                books=  [
                    {
                        "Title": row.get(mapping['title'], '').strip(),
                        "Author":row.get(mapping['author'],'').strip(),
                        "Rating":row.get(mapping['rating'],'').strip()
                     }
                    for row in reader if row.get(mapping['title'])
                ]
                self.bookshelf.extend(books)
                self.sort_shelf()
        except Exception as e:
            print(f"Error reading {source} file {file_path}: {e}")

    def sort_shelf(self):
        self.all_books = [book for id, book in enumerate(self.bookshelf) if book not in self.bookshelf[id+1:]]
        seen = set()
        unique_books = []
        for book in self.bookshelf:
            key= (book["Title"].lower(),book["Author"].lower())
            if key not in seen:
                seen.add(key)
                unique_books.append(book)
        self.all_books = unique_books



