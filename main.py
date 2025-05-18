
from book_shelf import BookShelf
from user_info import UserInfo
from website import create_app

app = create_app()


if __name__ == '__main__':
    app.run(debug=True,threaded=True)

def get_user_info(story_graph = False, good_reads=False):
    user = UserInfo()
    if story_graph:
        user.story_graph_csv("story_graph.csv")
    if good_reads:
        user.good_reads_csv("goodreads_library_export.csv")
    return user

def get_recs(book_shelf=None, genres=None):
    if book_shelf is None:
        book_shelf = []
    if genres is None:
        genres = []
    shelf = BookShelf()
    if book_shelf:
        return shelf.similar_books(book_shelf)
    if genres:
        return shelf.books_from_subjects(genres)
    return []



