import requests
import csv
import json

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

    def save_recs(self):
        file = "recommendations.csv"
        fields = ['Key', 'Title', 'Author', 'Subjects']
        with open(file, 'w', encoding='utf-8') as rec_file:
            csvwriter = csv.writer(rec_file)
            csvwriter.writerow(fields)
            for book in self.recommendations:
                csvwriter.writerow([book['key'], book['title'], book['author'], book['subject']])
        data = {
            "subjects": self.subjects,
            "books": self.recommendations
        }
        json_file = "recommendations.json"
        with open(json_file, 'w', encoding='utf-8') as rec_file:
            json.dump(data, rec_file, indent=4)
        return data

    def similar_books(self,books):
        for book in books:
            self.book_info(book)
        self.set_subjects()
        for subject in self.subjects:
            self.search_subject(subject)
        print(self.subjects)
        self.set_recs()
        return self.save_recs()

    def books_from_subjects(self,subjects):
        self.subjects = subjects
        for subject in self.subjects:
            self.search_subject(subject)
        self.set_recs()
        return self.save_recs()

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
        to_delete = ["Romans, nouvelles", "Fiction", "Large type books", "General",
                     "Novela"]
        subject_tally = dict((i, self.subjects.count(i)) for i in self.subjects)
        all_subjects = sorted(subject_tally.items(), key=lambda item: item[1], reverse=True)
        new_subjects = [subject for subject, tally in all_subjects if subject not in to_delete and tally > 3]
        self.subjects = new_subjects[:15]


    def search_subject(self, subject):
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
                    if 'isbn' in book:
                        print(book['title'])
                        edited_book = {
                            'title': book['title'],
                            'isbn':book['isbn'],
                            'author':book.get('author_name',[])[0],
                            'key':book['key'],
                            'gutenberg_url':book.get("id_project_gutenberg",[]),
                            'standard_ebook':book.get("id_standard_ebooks",[]),
                            'librivox':book.get("id_librivox",[]),
                            'openstax':book.get("id_open_stax",[]),
                            'edition_key':book.get('edition_key',''),
                            'lending':book.get('lending_edition_s',''),
                            'subject': book.get('subject',''),
                            'shared_subjects':shared_subjects }
                        self.recommendations.append(edited_book)

    def check_if_owned(self,book):
            isbn = any(element in book['isbn'] for element in self.isbn_list)
            edition_key = any(element in book['edition_key'] for element in self.edition_keys)
            key = True if book['key'] in self.keys else False
            title = True if book['title'] in self.owned_books else False
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
            item.pop('isbn',None)
            item.pop('edition_key',None)
        self.recommendations = sorted(new_recommendations, reverse=True, key=lambda d: len(d['shared_subjects']))[:10]