import difflib

import requests

from rapidfuzz import fuzz

class BookShelf:
    def __init__(self):
        self.bookshelf = []
        self.isbn_list = []
        self.recommendations = []
        self.recommendations_isbn = []
        self.edition_keys = []
        self.keys = []
        self.owned_books = []
        self.subjects = []


    def books_from_subjects(self, subjects):
        self.subjects = [subject.name for subject in subjects]
        self.set_subjects()
        print(self.subjects)
        for subject in self.subjects:
            self.search_subject(subject)
        print("finished searching!")

        self.set_recs()

    def book_info(self, book):
        url = f"https://openlibrary.org/search.json?title={book['Title']}&author={book['Author']}&fields=edition_key,title,subject,isbn,author_name,key"
        search = requests.get(url)
        result = search.json()
        found_books = []
        for search_book in result['docs']:
            if book['Title'] in search_book['title'] and book['Author'] in search_book['author_name']:
                book_object = {
                    "Title": search_book.get("title", []),
                    "Author": search_book.get("author_name", [])[0],
                    "Key": search_book.get("key", []),
                    "Subjects": search_book.get("subject", [])
                }
                self.subjects += search_book.get("subject", [])
                self.isbn_list += search_book.get("isbn", [])
                self.edition_keys += search_book.get("edition_key", [])
                self.keys.append(search_book.get("key", []))
                found_books.append(book_object)
        if len(found_books) > 0:
            titles = [book['Title'] for book in found_books]
            closest_title = difflib.get_close_matches(book['Title'], titles)
            if closest_title:
                match = titles.index(closest_title[0])
                self.owned_books.append(found_books[match])


    def set_subjects(self):
        to_delete = ["Romans, nouvelles", "Fiction", "Large type books", "General",
                     "Novela"]
        subject_tally = dict((i, self.subjects.count(i)) for i in self.subjects)
        all_subjects = sorted(subject_tally.items(), key=lambda item: item[1], reverse=True)
        new_subjects = [subject for subject, tally in all_subjects if subject not in to_delete]
        if len(new_subjects) > 20:
            clusters = []
            for subject in new_subjects:
                placed = False
                for cluster in clusters:
                    if fuzz.partial_ratio(subject, cluster) >= 85:
                        placed = True
                        break
                if not placed:
                    clusters.append(subject)
            self.subjects = clusters[:15]
        else:
            self.subjects = new_subjects[:15]

    def search_subject(self, subject):
        print(subject)
        url = (f"https://openlibrary.org/search.json?subject={subject}&fields="
               f"title,subject,isbn,key,edition_key,author_name,"
               f"id_project_gutenberg,id_openstax,id_librivox,lending_edition_s")
        search = requests.get(url)
        if 'application/json' in search.headers.get('Content-Type', ''):
            search_json = search.json()
            books = search_json['docs']
            for book in books:
                if "subject" in book:
                    all_subjects = [subject for subject in book['subject']]
                    shared_subjects = [subject for subject in all_subjects if subject in self.subjects]
                    if len(book.get('author_name',[])) > 0:
                        edited_book = {
                            'Title': book.get("title",[]),
                            'Author': book.get('author_name', [])[0],
                            'Key': book.get("key",[]),
                            'gutenberg_url': book.get("id_project_gutenberg", []),
                            'standard_ebook': book.get("id_standard_ebooks", []),
                            'librivox': book.get("id_librivox", []),
                            'openstax': book.get("id_open_stax", []),
                            'edition_key': book.get('edition_key', ''),
                            'lending': book.get('lending_edition_s', ''),
                            'Subjects': book.get('subject', ''),
                            'shared_subjects': shared_subjects}
                        self.recommendations.append(edited_book)

    def check_if_owned(self, book):
        isbn = any(element in book['isbn'] for element in self.isbn_list)
        edition_key = any(element in book['edition_key'] for element in self.edition_keys)
        key = True if book['Key'] in self.keys else False
        title = True if book['Title'] in self.owned_books else False
        if not isbn and not key and not edition_key and not title:
            return False
        else:
            return True

    def set_recs(self):
        new_recommendations = []
        for book in self.recommendations:
            if not self.check_if_owned(book):
                if book not in new_recommendations:
                    new_recommendations.append(book)
        for item in new_recommendations:
            item.pop('isbn', None)
            item.pop('edition_key', None)
        self.recommendations = sorted(new_recommendations, reverse=True, key=lambda d: len(d['shared_subjects']))[:10]