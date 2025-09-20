import difflib
from typing import List, Dict

from models import UserBook, Book, UserSubject, Subject
from search import Search


class BookShelf:
    def __init__(self, session, user_id):
        self.session = session
        self.user_id = int(user_id)
        self.subjects: List[str] = []
        self.recommendations: List[Dict] = []
        self.obj_format = lambda result: [
            {'Title': book.get("title", []),
             'Author': book.get('author_name', ['Unknown'])[0],
             'Key': book.get("key", []),
             'Subjects': book.get('subject', []),
             'Edition': book.get("edition_key", [''])[0]}
            for book in result.get("docs", [])]

    def update_recs(self):
        self.sort_subjects()
        self.search_subjects_bulk()
        self.sort_books()
        return self.save_books()

    def sort_subjects(self):
        results = (self.session.query(UserSubject, Subject)
                         .join(Subject, UserSubject.subject_id == Subject.id)
                         .filter(UserSubject.user_id == self.user_id, UserSubject.is_recommended == True)
                         .all()
                         )

        subject_counts = {}
        for us in results:
            name = us.Subject.name if us.Subject else None
            if name:
                subject_counts[name] = subject_counts.get(name, 0) + 1

        sorted_subjects = sorted(subject_counts.items(), key=lambda item: item[1], reverse=True)
        top_subjects = [subject for subject, count in sorted_subjects[:10]]
        self.subjects = top_subjects

    def book_info(self, book:Dict)->Dict:
        url = (f"https://openlibrary.org/search.json?"
               f"title={book['Title']}&author={book['Author']}"
               f"&fields=edition_key,title,subject,isbn,author_name,key"
               )

        search = Search([url], self.obj_format)
        found_books = [
            b for b in search.results
            if book['Title'].lower() in b.get("Title", "").lower()
        ]
        if len(found_books) == 1:
            return found_books[0]

        titles = [b['Title'] for b in found_books]
        closest = difflib.get_close_matches(book['Title'], titles, n=1)
        return next((b for b in found_books if b["Title"] == closest[0]), None) if closest else None

    def search_subjects_bulk(self):
        url_set = [(f"https://openlibrary.org/search.json?subject={subject}&fields="
                    f"title,subject,isbn,key,edition_key,author_name")
                   for subject in self.subjects
                   ]
        search = Search(url_set, self.obj_format)

        for book in search.results:
            if book not in self.recommendations:
                self.recommendations.append(book)

    def sort_books(self):
        sorted_books = []
        seen = set()
        for book in self.recommendations:
            identifier = (book["Title"].lower(), book["Author"].lower())
            if identifier in seen:
                continue
            shared = [s for s in book.get("Subjects", []) if s in self.subjects]
            if not shared:
                continue
            book["shared_subjects"] = shared
            sorted_books.append(book)
            seen.add(identifier)
        final_books = self.check_if_read(sorted_books)
        self.recommendations = sorted(final_books, key=lambda b: len(b["shared_subjects"]), reverse=True)[:5]

    def check_if_read(self,books:List[Dict])->List[Dict]:
        final_books = []

        for book_data in books:
            user_book = (
                self.session.query(UserBook, Book)
                .join(Book, UserBook.book_id == Book.id)
                .filter(
                    UserBook.user_id == self.user_id,
                    Book.title == book_data['Title'],
                    Book.author == book_data['Author']
                )
                .first()
            )

            if not user_book:
                final_books.append(book_data)
        return final_books

    def save_books(self,books=None, is_read=False)-> bool:
        books = books or self.recommendations
        for book_data in books:
            db_book = (
                self.session.query(Book)
                .filter(
                    Book.title == book_data['Title'],
                    Book.author == book_data['Author']
                )
                .first()
            )

            if not db_book:
                db_book = Book(
                    title=book_data['Title'],
                    author=book_data['Author'],
                    link=f"https://openlibrary.org/book/{book_data['Key']}"
                )
                self.session.add(db_book)
                self.session.flush()

            raw_subjects = book_data.get('Subjects', [])
            subjects = []
            for s in raw_subjects:
                if len(s) > 250:
                    parts = [part.strip() for part in s.split(",") if len(part.strip()) < 250]
                    subjects += parts
                else:
                    subjects.append(s)

            for subject in subjects:
                db_subject = self.session.query(Subject).filter(Subject.name == subject).first()
                if not db_subject:
                    db_subject = Subject(name=subject)
                    self.session.add(db_subject)
                    self.session.flush()

                db_user_subject = self.session.query(UserSubject).filter(
                    UserSubject.user_id == self.user_id,
                    UserSubject.subject_id == db_subject.id
                ).first()

                if not db_user_subject:
                    db_user_subject = UserSubject(user_id=self.user_id, subject_id=db_subject.id)
                    self.session.add(db_user_subject)

            db_user_book = UserBook(user_id=self.user_id, book_id=db_book.id, is_read=is_read)
            self.session.add(db_user_book)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Error saving books: {e}")
            return False
        return True
