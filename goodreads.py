from utils import make_soup


class GoodReads:
    def __init__(self, user=str):
        self.user_url = (f"https://www.goodreads.com/review/list/{user}"
                         f"?order=d&shelf=read&sort=rating")
        self.bookshelf = []
        self.get_user()

    def get_books(self, url):
        soup = make_soup(url)
        books = soup.find_all(attrs={"class": "bookalike review"})
        link_list = [{"title":
                          book.find(attrs={"class": "field title"}).a.text.replace("\n", "").strip(),
                      "url":
                          "https://www.goodreads.com/" + book.a['href'],
                      "isbn":
                          book.find(attrs={"class": "field isbn"}).text.replace("\n", "").replace("isbn", "").strip()}
                     for book in books]
        return link_list

    def get_user(self):
        self.bookshelf = self.get_books(self.user_url)
