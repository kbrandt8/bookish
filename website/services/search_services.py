from functions.models import User,UserBook,db,Book,UserSubject,Subject
from functions.search import Search

def add_open_library_book(user_id, form):
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


def search_openlibrary_books( search_type: str, query: str, page):
    query = query.strip()
    if not query:
        return []
    url = f"https://openlibrary.org/search.json?{search_type}={query}&fields=title,author_name,key,subject,edition_key&page={page}"
    obj_format = lambda result: [
        {'Title': book.get("title", []),
         'Author': book.get('author_name', ['Unknown'])[0],
         'Key': book.get("key", []),
         'Subjects': book.get('subject', []),
         'Edition': book.get("edition_key", [''])[0]}
        for book in result.get("docs", [])]
    search = Search([url], obj_format)
    num_found = search.results_raw[0].get("numFound", 0)
    return {
        "num_found": num_found,
        "books": search.results
    }