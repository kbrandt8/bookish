from operator import truediv

import requests
from collections import defaultdict

class BookShelf:
    def __init__(self,books):
        self.books = books
        self.subjects = defaultdict(int)
        self.bookshelf = []
        self.isbn_list = []
        self.recommendations = []
        for book in self.books:
            book_json = self.book_info(book)
            if book_json is not None:
                 self.bookshelf.append(book_json)
        self.set_isbn_list()
        self.set_subjects()
        print(self.bookshelf)
        print(self.subjects)
        for subject in self.subjects:
            self.search_subject(subject)



    def book_info(self,book):
        url=f"https://openlibrary.org/api/volumes/brief/isbn/{book['ISBN']}.json"
        search = requests.get(url)
        result = search.json()
        if result != []:
            book_id = next(iter(result['records']), None)
            book_info = result['records'][book_id]['data']
            book_json = {'ISBN':book['ISBN'], 'Title':book['Title'], 'Author':book['Author'],'Subjects':book_info.get('subjects',[])}
            return book_json
        else:
            return


    def set_subjects(self):
        for book in self.bookshelf:
            if "Subjects" in book:
                for subject in book['Subjects']:
                    self.subjects[subject['name']] += 1
        all_subjects = sorted(self.subjects.items(), key=lambda item: item[1], reverse=True)
        self.subjects= [subject for subject,tally in all_subjects if tally > 5]


    def search_subject(self,subject):
        url = f"https://openlibrary.org/search.json?subject={subject}&fields=edition_key,title,subject,isbn"
        search = requests.get(url)
        if 'application/json' in search.headers.get('Content-Type', ''):
            print(search.headers.get('Content-Type')+"\n")
            search_json = search.json()
            books = search_json['docs']
            for book in books:
                if "subject" in book:
                    all_subjects=[subject for subject in book['subject']]
                    shared_subjects = [subject for subject in all_subjects if subject in self.subjects]
                    if len(shared_subjects) >= 4 and 'isbn' in book and not self.check_if_owned(book['isbn']):
                        self.recommendations.append(book)
                        print(book['title'] + " has shared subjects: \n")
                        print(shared_subjects)
                        print("\n\n")




    def rec_details(self,key):
        url3 = f"https://openlibrary.org/{key}.json?details=true"

    def check_if_owned(self,isbn):
        for number in isbn:
            if number in self.isbn_list:
                return True
            else:
                return False
    def set_isbn_list(self):
        self.isbn_list = [book['ISBN'] for book in self.bookshelf]







