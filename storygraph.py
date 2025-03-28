import requests
from bs4 import BeautifulSoup
class StoryGraph():
    def __init__(self,user=str):
        self.user_url = f"https://app.thestorygraph.com/five_star_reads/{user}"
        self.bookshelf = []
        self.get_user()
    def make_soup(self,url):
        header = {'User-Agent':
                      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/44.0.2403.157 Safari/537.36',
                  'Accept-Language': 'en-US, en;q=0.5'}
        link = requests.get(url, headers=header)
        soup = BeautifulSoup(link.content, "html.parser")
        return soup

    def get_books(self):
        soup = self.make_soup(self.user_url)
        books = soup.find_all(attrs={"class": "book-title-author-and-series"})
        link_list = [{"title": book.a.text, "url": book.a['href']} for book in books]
        return link_list

    def get_isbn(self,url):
        soup = self.make_soup(f"https://app.thestorygraph.com/{url}")
        isbn = soup.find(attrs={"class": "edition-info"}).p
        return isbn.text.split(":")[1].strip()

    def get_user(self):
        self.bookshelf = self.get_books()
        for book in self.bookshelf:
            book['isbn'] = self.get_isbn(book['url'])

