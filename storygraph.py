from utils import make_soup
from bs4 import BeautifulSoup
class StoryGraph():
    def __init__(self,user=str):
        self.user_url = f"https://app.thestorygraph.com/five_star_reads/{user}"
        self.bookshelf = []
        self.get_user()

    def get_books(self,url):
        soup = make_soup(url)
        books = soup.find_all(attrs={"class": "book-title-author-and-series"})
        link_list = [{"title": book.a.text, "url": book.a['href']} for book in books]
        return link_list

    def get_isbn(self,url):
        soup = make_soup(f"https://app.thestorygraph.com/{url}")
        isbn = soup.find(attrs={"class": "edition-info"}).p
        return isbn.text.split(":")[1].strip()

    def get_user(self):
        self.bookshelf = self.get_books(self.user_url)
        for book in self.bookshelf:
            book['isbn'] = self.get_isbn(book['url'])

