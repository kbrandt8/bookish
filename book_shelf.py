import requests


class BookShelf:
    def __init__(self, books):
        self.books = books
        self.subjects = []
        self.bookshelf = []
        self.isbn_list = []
        self.recommendations = []
        self.recommendations_isbn = []
        for book in self.books:
            self.book_info(book)
        self.set_subjects()
        for subject in self.subjects:
            self.search_subject(subject)
        for key, book in enumerate(self.recommendations):
            if self.check_if_owned(book):
                print(book['title'])
                self.recommendations.remove(self.recommendations[key])



    def book_info(self, book):
        url = f"https://openlibrary.org/search.json?title={book['Title']}&author={book['Author']}&fields=edition_key,title,subject,isbn,author"
        search = requests.get(url)
        result = search.json()
        for search_book in result['docs']:
            if search_book['title'] == book['Title']:
                self.subjects += search_book.get("subject", [])
                self.isbn_list += search_book.get("isbn", [])

    def set_subjects(self):
        to_delete = ["Romans, nouvelles", "Fiction", "Large type books", "General", "Children's fiction",
                     "Reading Level-Grade 11", "Reading Level-Grade 12"]
        subject_tally = dict((i, self.subjects.count(i)) for i in self.subjects)
        all_subjects = sorted(subject_tally.items(), key=lambda item: item[1], reverse=True)
        new_subjects = [subject for subject, tally in all_subjects if subject not in to_delete and tally > 3]
        self.subjects = new_subjects

    def search_subject(self, subject):
        url = f"https://openlibrary.org/search.json?subject={subject}&fields=title,subject,isbn"
        search = requests.get(url)
        if 'application/json' in search.headers.get('Content-Type', ''):
            search_json = search.json()
            books = search_json['docs']
            for book in books:
                if "subject" in book:
                    all_subjects = [subject for subject in book['subject']]
                    shared_subjects = [subject for subject in all_subjects if subject in self.subjects]
                    if len(shared_subjects) > 4 and 'isbn' in book:
                        self.recommendations.append(book)

    def check_if_owned(self, book):
        for owned_book in self.bookshelf:
            if book['title'] == owned_book['Title']:
                print(f"{book['title']} == {owned_book['Title']}")
                return True
            elif book['title'] in owned_book['Title']:
                print(f"{book['title']} in {owned_book['Title']}")
                return True
            elif owned_book['Title'] in book['title']:
                print(f"  {owned_book['Title']} in {book['title']}")
                return True
            elif self.check_isbn(book['isbn']):
                print("isbn")
                return True

            return False

    def check_isbn(self, isbn):
        return any(element in isbn for element in self.isbn_list)
