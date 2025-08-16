import csv
from io import StringIO
from typing import List, Dict

class UserInfo:
    def __init__(self):
        self.bookshelf: List[Dict[str, str]] = []
        self.all_books: List[Dict[str, str]] = []

    def load_csv(self, file_storage, source: str):

        field_map = {
            "sg": {"title": "Title", "author": "Authors", "rating": "Star Rating"},
            "gr": {"title": "Title", "author": "Author", "rating": "My Rating"},
        }

        if source not in field_map:
            raise ValueError(f"Unsupported source '{source}'")

        mapping = field_map[source]

        try:
            # Read file in-memory
            stream = StringIO(file_storage.stream.read().decode("utf-8", errors="ignore"))
            reader = csv.DictReader(stream)

            books = []
            for row in reader:
                title = (row.get(mapping["title"], "") or "").strip()
                author = (row.get(mapping["author"], "") or "").strip()
                rating = (row.get(mapping["rating"], "") or "").strip()

                if not title:
                    continue

                books.append({"Title": title, "Author": author, "Rating": rating})

            self.bookshelf.extend(books)
            self.sort_shelf()

        except Exception as e:
            print(f"Error reading {source} file upload: {e}")

    def sort_shelf(self):
        seen = set()
        unique_books = []

        for book in self.bookshelf:
            key = (book["Title"].lower(), book["Author"].lower())
            if key not in seen:
                seen.add(key)
                unique_books.append(book)

        self.all_books = unique_books
