import requests
class BookShelf:
    def __init__(self):
        pass

    def book_info(self,isbn):
        url=f"https://openlibrary.org/api/volumes/brief/isbn/{isbn}.json"
        print(url)
        search = requests.get(url)
        book = search.json()
        book_id = next(iter(book['records']), None)
        book_info = book['records'][book_id]
        return book_info






