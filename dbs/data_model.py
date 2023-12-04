from peewee import *
from playhouse.sqlite_ext import FTS5Model, FTSModel, SqliteExtDatabase, SearchField
from config import ProjectConfig
from datetime import datetime
import tools.tg_bot_utils as tg_bot_utils

db_name = ProjectConfig.PATH_DBS+ProjectConfig.DB_NAME
db = SqliteExtDatabase(db_name, pragmas=(
    ('cache_size', -1024 * 64),  # 64MB page-cache.
    ('journal_mode', 'wal'),  # Use WAL-mode (you should always use this!).
    ('foreign_keys', 1)))


class PostIndex(FTS5Model):
    text = SearchField()
    class Meta:
        database = db
        options = {'tokenize': 'porter'}

# def get_post_index(post_key: int):
#     try:
#         queryes=[]
#         queryes.append(PostIndex. == post_key)
#         el = PostIndex.get(*queryes)
#         return el
#     except Exception as ex:
#         return None

class Post(Model):
    post_id = IntegerField()
    source_id = IntegerField(index=True)
    text = IntegerField(index=True)
    views = IntegerField()
    old_views = IntegerField()
    likes = IntegerField(index=True)
    dt = DateTimeField(index=True)
    in_telegraph = IntegerField()
    telegraph_url = CharField()
    text_hash = TextField(index=True)
    class Meta:
        database = db

# class PostIndex(FTSModel):
#     text = SearchField()
#     class Meta:
#         database = db
#         options = {'content': Post.text}

def get_post(post_id: int = 0, source_id: int = 0, text_hash: str = ''):
    try:
        queryes=[]
        if post_id!=0:
            queryes.append(Post.post_id == post_id)
        if source_id != 0:
            queryes.append(Post.source_id == source_id)
        if text_hash!='':
            queryes.append(Post.text_hash == text_hash)
        el = Post.get(*queryes)
        return el
    except Exception as ex:
        return None


def get_post_for_text_id(text_id: int) -> Post:
    try:
        queryes=[]
        queryes.append(Post.text == text_id)
        el = Post.get(*queryes)
        return el
    except Exception as ex:
        return None

def increase_post_views(post: Post):
    post.views += 1
    post.save()

class Hashtag(Model):
    value = CharField()
    class Meta:
        database = db

def get_hashtag(hashtag: str):
    try:
        queryes = []
        queryes.append(Hashtag.value == hashtag)
        el = Hashtag.get(*queryes)
        return el
    except Exception as ex:
        return None

class Post_Hashtag(Model):
    post = ForeignKeyField(Post, backref='post_hashtag')
    hashtag = ForeignKeyField(Hashtag, backref='post_hashtag', index=True)
    class Meta:
        database = db

def get_post_hashtags_str(post: Post) -> str:
    phs = Post_Hashtag.select().where(Post_Hashtag.post==post)
    hashtags = ''
    for ph in phs:
        htg = ph.hashtag.value
        hashtags = f'{hashtags}, {htg}'
    return hashtags[2:]

# class Link(Model):
#     owner = ForeignKeyField(Post, backref='links', index=True)
#     url = TextField()
#     caption = TextField()
#     class Meta:
#         database = db
#
# def get_post_link(post: Post) -> Link:
#     try:
#         queryes=[]
#         queryes.append(Link.owner == post)
#         el = Link.get(*queryes)
#         return el
#     except Exception as ex:
#         return None

class Photo(Model):
    owner = ForeignKeyField(Post, backref='photos', index=True)
    url = TextField()
    caption = TextField()
    class Meta:
        database = db

def get_post_photo(post: Post) -> Photo:
    try:
        queryes=[]
        queryes.append(Photo.owner == post)
        el = Photo.get(*queryes)
        return el
    except Exception as ex:
        return None

class User(Model):
    tg_user_id = IntegerField(index=True)
    username = CharField()
    firstname = CharField()
    lastname = CharField()
    first_visit = DateTimeField()
    last_visit = DateTimeField()
    last_post_read = ForeignKeyField(Post, backref='user', null=True)
    last_hashtag_read = ForeignKeyField(Hashtag, backref='user', null=True)
    class Meta:
        database = db

def get_user(user_key = 0, user_tg_id = 0, user_name = '') -> User:
    try:
        queryes = []
        if user_key != 0:
            queryes.append(User.id == user_key)
        if user_tg_id != 0:
            queryes.append(User.tg_user_id == user_tg_id)
        if user_name != '':
            queryes.append(User.username == user_name)
        el = User.get(*queryes)
        return el
    except Exception as ex:
        return None

def check_user(user_tg_id: int, username: str = '', firstname = '', lastname = ''):
    user = get_user(user_tg_id=user_tg_id)
    ts_now = datetime.now().replace(microsecond=0)
    ts_now = ts_now.timestamp()
    if user == None:
        user = User.create(tg_user_id=user_tg_id, username=username, firstname=firstname, lastname=lastname,
                           first_visit=ts_now, last_visit=0)
    else:
        user.last_visit = ts_now
    user.save()
    return user


class User_Post(Model):
    # Посты, которые пользователи добавили в избранное
    user = ForeignKeyField(User, backref='user_post', index=True)
    post = ForeignKeyField(Post, backref='user_post')
    class Meta:
        database = db

def check_user_post(user: User, post: Post) -> User_Post:
    try:
        queryes = []
        queryes.append(User_Post.user == user)
        queryes.append(User_Post.post == post)
        el = User_Post.get(*queryes)
        return el
    except Exception as ex:
        return None

def get_user_posts(user: User = None) -> User_Post:
    # task = Task.select().where(Task.id == 1).get()
    try:
        res = Post.select().join(User_Post).where(User_Post.user == user)
        return res
    except Exception as ex:
        return None

def get_user_posts_count(user: User = None) -> int:
    # task = Task.select().where(Task.id == 1).get()
    try:
        res = Post.select().join(User_Post).where(User_Post.user == user).count()
        return res
    except Exception as ex:
        return 0

def del_user_posts(post_obj: Post):
    try:
        user_favorites = User_Post.delete().where(User_Post.post == post_obj)
        user_favorites.execute()
    except Exception as ex:
        return None

# def rebuild_index():
#     PostIndex.rebuild()
#     PostIndex.optimize()

class Offer_Post(Model):
    # Посты, которые пользователи добавили в избранное
    user = ForeignKeyField(User, backref='offer_post', index=True)
    text = TextField()
    img_url = TextField()
    dt = DateTimeField()
    class Meta:
        database = db

def create_data_model():
    try:
        FTS5Model.fts5_installed()
        db.create_tables([Post, PostIndex])
    except Exception as ex:
        pass
    db.create_tables([Hashtag, Post_Hashtag, Photo, User, User_Post, Offer_Post])
    #rebuild_index()

