
import enum

class Errors(enum.Enum):
    NoError = 0
    PyError = -1
    ParserNotSupported = 1
    CantSaveReport = 2
    CantSavePosts = 3
    ParserNotFound  = 4
    PostsAnalisisError = 5
    TelegraphError = 6
    PostNotFound = 7
    NoGoodPost = 8