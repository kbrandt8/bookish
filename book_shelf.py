import requests
class BookShelf:
    def __init__(self,books):
        self.books = books
        for book in books:
           self.book_info(book['ISBN'])

    def book_info(self,isbn):
        url=f"https://openlibrary.org/api/volumes/brief/isbn/{isbn}.json"
        search = requests.get(url)
        book = search.json()
        if book != []:
            print(url)
            book_id = next(iter(book['records']), None)
            book_info = book['records'][book_id]['data']
            print(book_info['title'])
            items = book['items']
            if len(items) > 0:
                print(items)
            return book_info
        return "Not found in Open Library"








