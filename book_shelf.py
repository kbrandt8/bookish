import requests
import csv

class BookShelf:
    def __init__(self, books):
        self.books = books
        self.subjects = []
        self.bookshelf = []
        self.isbn_list = []
        self.recommendations = []
        self.recommendations_isbn = []
        self.edition_keys = []
        self.keys = []
        self.owned_books = []
        self.book_info({'Title':'Dracula','Author':'Bram Stoker'})

    def get_recs(self):
        for book in self.books:
            self.book_info(book)
        self.set_subjects()
        for subject in self.subjects:
            self.search_subject(subject)
        self.set_recs()
        file = "recommendations.csv"
        fields = ['Title','Subjects','Key']
        with open (file,'w',encoding='utf-8') as rec_file:
            csvwriter = csv.writer(rec_file)
            csvwriter.writerow(fields)
            for book in self.recommendations:
                csvwriter.writerow([book['title'],book['key'],book['subject']])

    def book_info(self, book):
        url = f"https://openlibrary.org/search.json?title={book['Title']}&author={book['Author']}&fields=edition_key,title,subject,isbn,author_name,key"
        search = requests.get(url)
        result = search.json()
        for search_book in result['docs']:
            if book['Title'] in search_book['title']  and book['Author'] in search_book['author_name']:
                self.owned_books.append(book['Title'])
                self.subjects += search_book.get("subject", [])
                self.isbn_list += search_book.get("isbn", [])
                self.edition_keys += search_book.get("edition_key",[])
                self.keys.append(search_book.get("key",[]))


    def set_subjects(self):
        to_delete = ["Romans, nouvelles", "Fiction", "Large type books", "General", "Children's fiction",
                     "Novela"]
        subject_tally = dict((i, self.subjects.count(i)) for i in self.subjects)
        all_subjects = sorted(subject_tally.items(), key=lambda item: item[1], reverse=True)
        new_subjects = [subject for subject, tally in all_subjects if subject not in to_delete and tally > 3]
        self.subjects = new_subjects

    def search_subject(self, subject):
        url = f"https://openlibrary.org/search.json?subject={subject}&fields=title,subject,isbn,key,edition_key,author_name"
        search = requests.get(url)
        if 'application/json' in search.headers.get('Content-Type', ''):
            search_json = search.json()
            books = search_json['docs']
            for book in books:
                if "subject" in book:
                    all_subjects = [subject for subject in book['subject']]
                    shared_subjects = [subject for subject in all_subjects if subject in self.subjects]
                    if len(shared_subjects) > 4 and 'isbn' in book:
                        edited_book = {'title': book['title'],'isbn':book['isbn'],'key':book['key'],'edition_key':book['edition_key'],'subject':[subject for subject in book['subject'] if subject in self.subjects]}
                        self.recommendations.append(edited_book)

    def set_recs(self):
        new_recommendations = []
        for key, book in enumerate(self.recommendations):
            isbn = any(element in book['isbn'] for element in self.isbn_list)
            edition_key = any(element in book['edition_key'] for element in self.edition_keys)
            key = True if book['key'] in self.keys else False
            title = True if book['title'] in self.owned_books else False
            if not isbn and not key and not edition_key and not title and book not in new_recommendations:
                    new_recommendations.append(book)
        self.recommendations = sorted(new_recommendations, reverse=True, key=lambda d: len(d['subject']))