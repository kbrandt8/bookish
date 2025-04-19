import requests
from collections import defaultdict

class BookShelf:
    def __init__(self,books):
        self.books = books
        self.subjects = defaultdict(int)
        self.bookshelf = []
        self.recommendations = []
        for book in self.books:
            book_json = self.book_info(book['ISBN'])
            if book_json is not None:
                 self.bookshelf.append(book_json)
        self.set_subjects()
        print(self.subjects)
        for subject in self.subjects:
            print(subject)
            self.search_subject(subject)
        for book in self.recommendations:
            print(book['title'])

    def book_info(self,isbn):
        url=f"https://openlibrary.org/api/volumes/brief/isbn/{isbn}.json"
        search = requests.get(url)
        book = search.json()
        if book != []:
            book_id = next(iter(book['records']), None)
            book_info = book['records'][book_id]['data']
            return book_info
        else:
            return


    def set_subjects(self):
        for book in self.bookshelf:
            if "subjects" in book:
                for subject in book['subjects']:
                    self.subjects[subject['name']] += 1
        all_subjects = sorted(self.subjects.items(), key=lambda item: item[1], reverse=True)
        self.subjects= [subject for subject,tally in all_subjects if tally >1]


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
                    if len(shared_subjects) >= 3:
                        self.recommendations.append(book)
                        # print(book['title'] + " has shared subjects: \n")
                        # print(shared_subjects)
                        # print("\n\n")




    def rec_details(self,key):
        url3 = f"https://openlibrary.org/{key}.json?details=true"





