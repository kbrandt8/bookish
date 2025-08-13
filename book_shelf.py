import difflib
from typing import List, Dict

from search import Search
from website.models import db, UserSubject, UserBook, Book, Subject


class BookShelf:
    def __init__(self):
        self.recommendations: List[Dict] = []
        self.subjects: List[str] = []
        self.obj_format = lambda result: [
            {'Title': book.get("title", []),
             'Author': book.get('author_name', ['Unknown'])[0],
             'Key': book.get("key", []),
             'Subjects': book.get('subject', []),
             'Edition': book.get("edition_key", [''])[0]}
            for book in result.get("docs", [])]

    def is_new_user(self, user_id: int) -> bool:
        return not db.session.query(
            db.exists().where(UserSubject.user_id == user_id)
        ).scalar()

    def sort_subjects(self, user_id):
        user_books = db.session.execute(
            db.select(UserBook)
            .where(UserBook.user_id == user_id, UserBook.is_recommended == False)
            .options(db.joinedload(UserBook.book).joinedload(Book.subjects))
        ).scalars().unique()
        subject_counts = {}
        for user_book in user_books:
            for subject in user_book.book.subjects:
                subject_counts[subject] = subject_counts.get(subject, 0) + 1
        least_fav_subjects = [s for s, count in subject_counts.items() if count > 3]
        for subject in least_fav_subjects:
            user_subject = db.session.execute(
                db.select(UserSubject)
                .where(UserSubject.user_id == user_id, UserSubject.subject_id == subject.id)
            ).scalar()

            if user_subject:
                user_subject.is_recommended = False
            else:
                db.session.add(UserSubject(
                    user_id=user_id,
                    subject_id=subject.id,
                    is_recommended=False
                ))
            db.session.commit()

    def get_subjects(self, user_id):
        user_subjects = db.session.execute(
            db.select(UserSubject)
            .where(
                UserSubject.user_id == user_id,
                UserSubject.is_recommended == True
            )
            .options(db.joinedload(UserSubject.subject))
        ).scalars().all()

        subject_counts = {}
        for us in user_subjects:
            name = us.subject.name if us.subject else None
            if name:
                subject_counts[name] = subject_counts.get(name, 0) + 1

        sorted_subjects = sorted(subject_counts.items(), key=lambda item: item[1], reverse=True)
        top_subjects = [subject for subject, count in sorted_subjects[:20]]
        self.subjects = top_subjects
        return top_subjects

    def add_books(self, user_id, is_read=False, owned_books=None):
        books = owned_books if owned_books is not None else self.recommendations
        for book_data in books:
            title, author = book_data["Title"], book_data["Author"]
            link = f"https://openlibrary.org{book_data['Key']}"
            raw_subjects = book_data.get('Subjects', [])
            print(title)
            # Split long subject strings
            subjects = []
            for s in raw_subjects:
                if len(s) > 250:
                    print(f"{s}: {len(s)}")
                    parts = [part.strip() for part in s.split(",") if len(part.strip()) < 250]
                    subjects += parts
                else:
                    subjects.append(s)

            book = Book.query.filter_by(title=title, author=author).first()
            if not book:
                book = Book(title=title, author=author, link=link)
                db.session.add(book)
                db.session.flush()

            if is_read:
                for s in subjects:
                    if not s:
                        continue

                    subject = Subject.query.filter_by(name=s).first()
                    if not subject:
                        print(f" adding subject: {s}")
                        subject = Subject(name=s)
                        db.session.add(subject)
                        db.session.flush()

                    if subject not in book.subjects:
                        book.subjects.append(subject)

                    user_subject = UserSubject.query.filter_by(
                        user_id=user_id, subject_id=subject.id
                    ).first()
                    if not user_subject:
                        db.session.add(UserSubject(
                            user_id=user_id,
                            subject_id=subject.id
                        ))

            existing_userbook = UserBook.query.filter_by(user_id=user_id, book_id=book.id).first()
            if not existing_userbook:
                db.session.add(UserBook(user_id=user_id, book_id=book.id, is_read=is_read))

        db.session.commit()

    def book_info(self, book):
        url = (f"https://openlibrary.org/search.json?"
               f"title={book['Title']}&author={book['Author']}"
               f"&fields=edition_key,title,subject,isbn,author_name,key"
               )

        search = Search([url], self.obj_format)
        found_books = [
            search_book for search_book in search.results
            if book['Title'].lower() in search_book.get("Title", "").lower()
        ]
        if len(found_books) == 1:
            return found_books[0]

        titles = [book['Title'] for book in found_books]
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
        book_list = []
        seen = set()
        for book in self.recommendations:
            identifier = (book["Title"].lower(), book["Author"].lower())
            if identifier in seen:
                continue
            shared = [s for s in book.get("Subjects", []) if s in self.subjects]
            if not shared:
                continue
            book["shared_subjects"] = shared
            user_book = Book.query.filter_by(title=book['Title'], author=book['Author']).first()
            if user_book:
                continue
            book_list.append(book)
            seen.add(identifier)
            self.recommendations = sorted(book_list, key=lambda b: len(b["shared_subjects"]), reverse=True)[:15]
        for book in self.recommendations:
            print(book['Title'])

    def add_open_library_book(self, user_id, form):
        title = form.get("title")
        author = form.get("author")
        key = form.get("key")
        subjects = form.getlist("subjects")
        is_read = True if form.get("is_read") == "True" else False
        is_recommended = True if form.get("is_recommended") == "True" else False

        book = Book.query.filter_by(title=title, author=author).first()
        if not book:
            book = Book(title=title, author=author, link=f"https://openlibrary.org{key}")
            db.session.add(book)
            db.session.flush()

        for subject_name in subjects:
            if not subject_name:
                continue
            subject = Subject.query.filter_by(name=subject_name).first()
            if not subject:
                subject = Subject(name=subject_name)
                db.session.add(subject)
                db.session.flush()
            if subject not in book.subjects:
                book.subjects.append(subject)

            if not UserSubject.query.filter_by(user_id=user_id, subject_id=subject.id).first():
                db.session.add(
                    UserSubject(user_id=user_id, subject_id=subject.id, is_recommended=is_recommended))

        if not UserBook.query.filter_by(user_id=user_id, book_id=book.id).first():
            db.session.add(
                UserBook(user_id=user_id, book_id=book.id, is_read=is_read, is_recommended=is_recommended))

        db.session.commit()

    def search_openlibrary_books(self, search_type: str, query: str, page):
        query = query.strip()
        if not query:
            return []
        url = f"https://openlibrary.org/search.json?{search_type}={query}&fields=title,author_name,key,subject,edition_key&page={page}"
        search = Search([url], self.obj_format)
        num_found = search.results_raw[0].get("numFound", 0)
        return {
            "num_found": num_found,
            "books": search.results
        }
