import difflib

import requests

from website.models import db, UserSubject, UserBook, Book, Subject, User


class BookShelf:
    def __init__(self, user_id):
        self.user_id = user_id
        self.user = User.query.get(self.user_id)
        self.recommendations = []
        self.subjects = []

    def sort_subjects(self):
        user_books = db.session.execute(
            db.select(UserBook)
            .where(UserBook.user_id == self.user_id, UserBook.is_recommended == False)
            .options(db.joinedload(UserBook.book).joinedload(Book.subjects))
        ).scalars().unique()
        all_subjects = []
        for user_book in user_books:
            all_subjects.extend(user_book.book.subjects)
        tally = {}
        for subject in all_subjects:
            if subject in tally:
                tally[subject] += 1
            else:
                tally[subject] = 1
        sorted_tally = sorted(tally.items(), key=lambda item: item[1], reverse=True)
        not_recommended = [subject[0] for subject in sorted_tally if subject[1] > 3]
        for subject in not_recommended:
            user_subject = db.session.execute(
                db.select(UserSubject)
                .where(UserSubject.user_id == self.user_id, UserSubject.subject_id == subject.id)
            ).scalar()
            user_subject.is_recommended = False
        db.session.commit()

    def get_subjects(self):
        self.sort_subjects()

        user_subjects = db.session.execute(
            db.select(UserSubject)
            .where(
                UserSubject.user_id == self.user_id,
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

    def add_books(self):
        user = self.user
        if not user:
            print(f"User ID {self.user_id} not found.")
            return

        for book_data in self.recommendations:
            print(f"{book_data['Title']}")
            title = book_data['Title']
            author = book_data['Author']
            link = f"https://openlibrary.org{book_data['Key']}"
            subjects = book_data.get('Subjects', [])

            book = Book.query.filter_by(title=title, author=author).first()
            if not book:
                book = Book(title=title, author=author, link=link)
                db.session.add(book)
                db.session.flush()

            for subject_name in subjects:
                if not subject_name:
                    continue
                subject = Subject.query.filter_by(name=subject_name).first()
                if not subject:
                    print(f" adding subject: {subject_name}")
                    subject = Subject(name=subject_name)
                    db.session.add(subject)
                    db.session.flush()
                if subject not in book.subjects:
                    book.subjects.append(subject)
                user_subject = UserSubject.query.filter_by(
                user_id = self.user_id, subject_id = subject.id
                ).first()
                if not user_subject:
                    db.session.add(UserSubject(
                        user_id=self.user_id,
                        subject_id = subject.id
                    ))

            existing_userbook = UserBook.query.filter_by(user_id=user.id, book_id=book.id).first()
            if not existing_userbook:
                db.session.add(UserBook(user_id=user.id, book_id=book.id, is_read=False))

        db.session.commit()

    def books_from_subjects(self):
        print("Getting subjects...")
        self.get_subjects()
        print(f"Searching Subjects...\n")
        for subject in self.subjects:
            self.search_subject(subject)
        print(f"Sorting recommendations...")
        self.sort_books()
        print(f"Saving to database... \n")
        self.add_books()
        print("Enjoy your new recs!")

    def book_info(self, book):
        url = f"https://openlibrary.org/search.json?title={book['Title']}&author={book['Author']}&fields=edition_key,title,subject,isbn,author_name,key"
        search = requests.get(url)
        result = search.json()
        found_books = []
        for search_book in result['docs']:
            if book['Title'] in search_book['title'] and book['Author'] in search_book['author_name']:
                authors = search_book.get("author_name", [])
                author = authors[0] if authors else "Unknown"
                print(search_book.get("title", []))
                book_object = {
                    "Title": search_book.get("title", []),
                    "Author": author,
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

    def search_subject(self, subject):
        print(f"Searching: {subject}\n")
        url = (f"https://openlibrary.org/search.json?subject={subject}&fields="
               f"title,subject,isbn,key,edition_key,author_name,"
               f"id_project_gutenberg,id_openstax,id_librivox,lending_edition_s")
        search = requests.get(url)
        if 'application/json' in search.headers.get('Content-Type', ''):
            search_json = search.json()
            books = search_json['docs']
            for book in books:
                if "subject" in book:
                    authors = book.get('author_name', [])
                    author = authors[0] if authors else "unknown"
                    edited_book = {
                        'Title': book.get("title", []),
                        'Author': author,
                        'Key': book.get("key", []),
                        'Subjects': book.get('subject', ''),
                    }
                    if edited_book not in self.recommendations:
                        self.recommendations.append(edited_book)

    def sort_books(self):
        book_list = []
        for book in self.recommendations:
            user_book = Book.query.filter_by(title=book['Title'], author=book['Author']).first()
            if user_book:
                continue
            else:
                shared_subjects = [ subject for subject in book['Subjects'] if subject in self.subjects]
                book['shared_subjects'] = shared_subjects
                book_list.append(book)
        self.recommendations = sorted(book_list, key= lambda d:len(d['shared_subjects']), reverse=True)[:15]
        for book in self.recommendations:
            print(book['Title'])
