import mongoengine
from mongoengine import Document, StringField, DictField, ListField, BooleanField, DateTimeField
from mongoengine import IntField, FloatField
from flask_login import UserMixin
from config import config


mongoengine.connect(
    db=config["mongo"]["database"],
    username=config["mongo"]["username"],
    password=config["mongo"]["password"],
    host=f"mongodb://{config["mongo"]["host"]}:{config["mongo"]["port"]}"
)


class User(UserMixin, Document):
    meta = {"collection": "users"}

    display_name = StringField()
    username = StringField()
    discord = StringField()

    data = DictField(default={})
    options = DictField(default={})
    permissions = DictField(default={})
    tags = ListField(default=[])

    def __init__(self, username, discord, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = username
        self.discord = discord


class Quote(Document):
    meta = {"collection": "quotes"}
    quotes = ListField(StringField())
    users = ListField(StringField())
    enabled = BooleanField(default=True)

    guild_id = StringField(required=True)
    channel_id = StringField(required=True)
    message_id = StringField(required=True)

    dt = DateTimeField(required=True)
    added_by = StringField(required=True)


class Guild(Document):
    meta = {"collection": "guilds"}
    guild_id = StringField(required=True, unique=True, max_length=128)
    name = StringField(required=True, max_length=256)
    data = DictField(default={})


class WordleGame(Document):
    meta = {"collection": "wordle"}
    user_id = StringField(required=True, max_length=128)
    msg_id = IntField(required=True, unique=True)
    game = IntField(required=True)
    score = IntField(required=True)
    hard_mode = BooleanField(required=True)
    msg_content = StringField(required=True, max_length=1024)
    guesses = ListField(StringField(max_length=50))


class ZurdleGame(Document):
    meta = {"collection": "zurdle"}
    user_id = StringField(required=True, max_length=128)
    game = IntField(required=True)
    score = IntField(required=True)
    hard_mode = BooleanField(required=True)
    words = ListField(StringField(max_length=50))
    guesses = ListField(StringField(max_length=50))
    mode = StringField(required=True, max_length=20, default="daily")
    played_on = IntField()


class Changelog(Document):
    meta = {"collection": "changelog"}
    title = StringField(required=True, max_length=512)
    content = StringField(max_length=8192)
    date = DateTimeField()
    tags = ListField(StringField(max_length=32), default=[])
    user_id = StringField(required=True, max_length=128)

class Calendar(Document):
    meta = {"collection": "calendar"}
    year = IntField(required=True)
    user_id = StringField(required=True, max_length=128)
    days = DictField(default={})
