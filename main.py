from storygraph import StoryGraph
from goodreads import GoodReads
from book_shelf import BookShelf
from user_info import UserInfo

#storygraph functionality
user = UserInfo()
user.story_graph_csv("story_graph.csv")
# print(user.bookshelf)
user.good_reads_csv("goodreads_library_export.csv")
# print(user.bookshelf)

#Good Reads Functionality
# gr_user = GoodReads("189192928-kaitlyn")
# print(gr_user.bookshelf)

shelf = BookShelf(user.bookshelf)


