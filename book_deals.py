import requests
from website.services.user_service import user_book_deal

class BookDeal:
    def __init__(self,user,bookshelf):
        self.shelf = bookshelf
        self.user = user
        self.google_url = f"https://www.googleapis.com/books/v1/volumes?q="
        self.deals = []
        self.start()

    def start(self):
        for book in self.shelf:
            current_price = book.deal or float("inf")
            self.get_google_info(book)
            deals = sorted(self.deals, reverse=False, key=lambda d: d['price'])
            if len(deals) > 0 and deals[0]['price']< current_price:
                user_book_deal(self.user,deals[0])
            else:
                continue

    def get_google_info(self,book):
        url = f"{self.google_url}{book.book.title}"
        search = requests.get(url)
        results = search.json()
        for_sale = [{"title":book.book.title,
                     "id":book.book_id,
                     "price":item['saleInfo']['listPrice']['amount'],
                     "link":item['saleInfo']["buyLink"]
                     } for item in results.get("items")
                    if item['saleInfo']
                    and item['saleInfo']['saleability'] == "FOR_SALE"]
        on_sale = sorted(for_sale, reverse=False, key=lambda d: d['price'])
        if on_sale:
            self.deals.append(on_sale[0])
        else:
            return False


