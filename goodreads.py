import requests
import re
from bs4 import BeautifulSoup
class GoodReads():
    def __init__(self,user=str):
        self.user_url = (f"https://www.goodreads.com/review/list/{user}"
                         f"?order=d&shelf=read&sort=rating")
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
    def get_books(self,url):
        soup = self.make_soup(url)
        books = soup.find_all(attrs={"class": "bookalike review"})
        for book in books:
            isbn = book.find(attrs={"class":"field title"})
            title = book.find(attrs={"class":"field isbn"})


        link_list = [{"title":
                          book.find(attrs={"class":"field title"}).a.text.replace("\n","").strip(),
                      "url":
                          "https://www.goodreads.com/"+book.a['href'],
                     "isbn":
                          book.find(attrs={"class":"field isbn"}).text.replace("\n","").replace("isbn","").strip()}
                     for book in books]
        return link_list
    def get_user(self):
        self.bookshelf = self.get_books(self.user_url)