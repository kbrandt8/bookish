import requests
from models import UserBook, Book


class BookDeal:
    def __init__(self, user, bookshelf, session):
        self.shelf = bookshelf
        self.user = user
        self.session = session
        self.sources = [
            self.get_open_library_deal,
            self.get_google_deal,
        ]
        self.google_url = f"https://www.googleapis.com/books/v1/volumes?q="

        self.deals = []
        self.run()

    def run(self):
        for book in self.shelf:
            current_price = book.deal if book.deal is not None else float("inf")
            all_deals = []
            for source in self.sources:
                deal = source(book)
                if deal:
                    all_deals.append(deal)
            if all_deals:
                best_deal = min(all_deals, key=lambda d: d['price'])
                if best_deal['price'] < current_price:
                    self.user_book_deal(self.user, best_deal)

    def get_open_library_deal(self, book):
        try:
            url = (f"https://openlibrary.org/search.json?title={book.book.title}&author={book.book.author}"
                   f"&fields=title,author_name,identifiers,ebook_access,has_fulltext,id_project_gutenberg,"
                   f"id_librivox,id_standard_ebooks,lending_edition_s,lending_identifier_s"
                   )
            res = requests.get(url, timeout=6)
            data = res.json()
            for doc in data.get("docs", []):
                if doc.get("ebook_access") == "public":
                    if doc.get("id_standard_books"):
                        link = f"https://standardebooks.org/ebooks/{doc["id_standard_ebooks"][0]}"
                    elif doc.get("id_project_gutenberg"):
                        link = f"https://www.gutenberg.org/ebooks/{doc['id_project_gutenberg'][0]}"
                    else:
                        continue
                    return {
                        "title": book.book.title,
                        "id": book.book_id,
                        "price": 0.00,
                        "link": link,
                    }
        except Exception as e:
            print(f"[OpenLibrary Error] {e}")
        return None

    def get_google_deal(self, book):
        try:
            url = (f"https://www.googleapis.com/books/v1/volumes?"
                   f"q={book.book.title}")
            res = requests.get(url, timeout=6)
            data = res.json()
            items = data.get("items", [])
            deals = []
            for item in items:
                sale_info = item.get("saleInfo", {})
                if sale_info.get("saleability") == "FOR_SALE":
                    price = sale_info.get("listPrice", {}).get("amount")
                    link = sale_info.get("buyLink")
                    if price is not None and link:
                        deals.append({
                            "title": book.book.title,
                            "id": book.book_id,
                            "price": price,
                            "link": link
                        })
            return min(deals, key=lambda d: d['price'])
        except Exception as e:
            print(f"Google Books error: {e}")
        return None


    def user_book_deal(self, user_id, book):
        user_id = int(user_id)
        book_id =int(book['id'])
        user_book = (
            self.session.query(UserBook)
            .filter(
                UserBook.user_id == user_id,
                UserBook.book_id == book_id
            )
            .first()
        )
        user_book.deal = book['price']
        user_book.deal_link = book['link']
        self.session.commit()


