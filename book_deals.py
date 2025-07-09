import requests


class BookDeal:
    def __init__(self,bookshelf):
        self.shelf = bookshelf
        self.google_url = f"https://www.googleapis.com/books/v1/volumes?q="

    def get_google_info(self,book):
        url = f"{self.google_url}{book.book.title}"
        search = requests.get(url)
        results = search.json()
        for_sale = [item for item in results.get("items") if item['saleInfo'] and item['saleInfo']['saleability'] == "FOR_SALE"]
        on_sale = sorted(for_sale, reverse=False, key=lambda d: d['saleInfo']['listPrice']['amount'])
        return on_sale[0]


