from storygraph import StoryGraph
from goodreads import GoodReads
from book_shelf import BookShelf
from user_info import UserInfo

#storygraph functionality
user = UserInfo()
user.story_graph_csv("story_graph.csv")

user.good_reads_csv("goodreads_library_export.csv")

shelf = BookShelf(user.all_books)

