
from book_shelf import BookShelf
from user_info import UserInfo

#storygraph functionality
user = UserInfo()
user.story_graph_csv("story_graph.csv")
#good reads functionality
user.good_reads_csv("goodreads_library_export.csv")

shelf = BookShelf(user.all_books)
shelf.get_recs()

