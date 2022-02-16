from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, create_engine
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table
from sqlalchemy.sql import func
from sqlalchemy.orm import Session, sessionmaker

POSTGRES_LOGIN = 'postgres'
POSTGRES_PASSWORD = 'a26a15p17f'
POSTGRES_HOST = '127.0.0.1'
POSTGRES_PORT = '5432'
POSTGRESS_DB = 'postgres'

Base = declarative_base()
POSTGRES_URL = f'postgresql://{POSTGRES_LOGIN}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRESS_DB}'
engine = create_engine(POSTGRES_URL, echo=True)
Base = declarative_base()

StreamTag = Table('stream_tag', Base.metadata,
                  Column("stream_id", String, ForeignKey("stream.id"), primary_key=True),
                  Column("tag_id", String, ForeignKey("tag.id"), primary_key=True))

GameTag = Table('game_tag', Base.metadata,
                Column("game_id", String, ForeignKey("game.id"), primary_key=True),
                Column("tag_id", String, ForeignKey("tag.id"), primary_key=True))

ChatEmojis = Table('emoji_chat', Base.metadata,
                   Column("emoji_id", String, ForeignKey("emoji.id"), primary_key=True),
                   Column("chat_id", String, ForeignKey("chat.id"), primary_key=True))

ChatGifters = Table('chat_gifter', Base.metadata,
                    Column("user_id", String, ForeignKey("user.id"), primary_key=True),
                    Column("chat_id", String, ForeignKey("chat.id"), primary_key=True))

BroadcasterSubscription = Table('broadcaster_subscription', Base.metadata,
                                Column("user_id", String, ForeignKey("user.id"), primary_key=True),
                                Column("subscription_id", String, ForeignKey("subscription.id"), primary_key=True))

GifterSubscription = Table('gifter_subscription', Base.metadata,
                           Column("user_id", String, ForeignKey("user.id"), primary_key=True),
                           Column("subscription_id", String, ForeignKey("subscription.id"), primary_key=True))


class User(Base):
    __tablename__ = 'user'

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, onupdate=func.now())
    display_name = Column(String)
    login = Column(String)
    description = Column(String)
    offline_image_url = Column(String)
    profile_image_url = Column(String)
    viewer_count = Column(Integer)
    follower_count = Column(Integer)
    email = Column(String)
    user_created_at = Column(DateTime)

    team_id = Column(ForeignKey("team.id"))

    # streams? uselist false?
    stream = relationship("Stream", back_populates="user", uselist=False)
    team = relationship("Team", back_populates="users")
    created_clips = relationship("Clip", back_populates="creator", foreign_keys='Clip.creator_id')
    clips = relationship("Clip", back_populates="user", foreign_keys='Clip.user_id')
    messages = relationship("Message", back_populates="user")
    videos = relationship("Video", back_populates="user")
    b_subscriptions = relationship("Subscription", secondary=BroadcasterSubscription, back_populates="broadcasters")
    g_subscriptions = relationship("Subscription", secondary=GifterSubscription, back_populates="gifters")
    chats = relationship("Chat", secondary=ChatGifters, back_populates="top_gifters")

    def __repr__(self):
        return f"<{self.id}>"


class Subscription(Base):
    __tablename__ = 'subscription'

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, onupdate=func.now())
    is_gift = Column(Boolean)
    tier = Column(Integer)  # 1000 is tier 1, 2000 is tier 2, and 3000 is tier 3

    broadcaster_id = Column(ForeignKey("user.id"))
    gifter_id = Column(ForeignKey("user.id"))

    broadcasters = relationship("User", secondary=BroadcasterSubscription, back_populates="b_subscriptions")
    gifters = relationship("User", secondary=GifterSubscription, back_populates="g_subscriptions")


class Team(Base):
    __tablename__ = 'team'
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, onupdate=func.now())
    team_name = Column(String)
    team_display_name = Column(String)
    background_image_url = Column(String)
    description = Column(String)
    banner = Column(String)
    thumbnail_url = Column(String)
    team_created_at = Column(String)
    team_updated_at = Column(String)

    users = relationship("User", back_populates="team")

    def __repr__(self):
        return f"<Product({self.domain, self.modified_at})>"


class Video(Base):
    __tablename__ = 'video'

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, onupdate=func.now())
    video_type = Column(String)  # past_broadcast, highlight, upload
    title = Column(String)
    description = Column(String)
    video_created_at = Column(DateTime)
    video_published_at = Column(DateTime)
    url = Column(String)
    thumbnail_url = Column(String)
    viewable = Column(Boolean)
    view_count = Column(Integer)
    language = Column(String)
    duration = Column(DateTime)
    muted_segments = Column(ARRAY(JSON))  # offset : int, duration : int

    user_id = Column(String, ForeignKey('user.id'))
    game_id = Column(String, ForeignKey('game.id'))
    chat_id = Column(String, ForeignKey('chat.id'))

    user = relationship("User", back_populates="videos")
    game = relationship("Game", back_populates='videos')
    chat = relationship("Chat", back_populates="video", uselist=False)
    clips = relationship("Clip", back_populates="video")

    def __repr__(self):
        return f"<Video({self.id, self.created_at})>"


class Clip(Base):
    __tablename__ = "clip"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, onupdate=func.now())
    title = Column(String)
    url = Column(String)
    embed_url = Column(String)
    view_count = Column(Integer)
    thumbnail_url = Column(String)
    duration = Column(Integer)
    clip_created_at = Column(DateTime)

    user_id = Column(ForeignKey("user.id"))
    creator_id = Column(ForeignKey("user.id"))
    video_id = Column(ForeignKey("video.id"))

    creator = relationship("User", back_populates="created_clips", foreign_keys=[creator_id])
    user = relationship("User", back_populates="clips", foreign_keys=[user_id])
    video = relationship("Video", back_populates="clips")


class Stream(Base):
    __tablename__ = "stream"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, onupdate=func.now())
    stream_type = Column(String(4))  # "live" or ""
    title = Column(String)
    viewer_count = Column(String)
    started_at = Column(DateTime)
    language = Column(String)
    thumbnail_url = Column(String)
    is_mature = Column(Boolean)

    user_id = Column(ForeignKey("user.id"))
    tag_id = Column(ForeignKey("tag.id"))
    chat_id = Column(ForeignKey("chat.id"))
    banner_id = Column(ForeignKey("banner.id"))

    user = relationship("User", back_populates="stream", uselist=False)
    tags = relationship("Tag", secondary=StreamTag, back_populates="streams")
    chat = relationship("Chat", back_populates="stream", uselist=False)
    banners = relationship("Banner", back_populates="stream")


class Banner(Base):
    __tablename__ = "banner"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, onupdate=func.now())
    text = Column(String)
    link = Column(String)
    image_url = Column(String)

    stream = relationship("Stream", back_populates="banners")


class Game(Base):
    __tablename__ = "game"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, onupdate=func.now())
    name = Column(String)
    url = Column(String)
    description = Column(String)
    box_art_url = Column(String)
    viewer_count = Column(Integer)
    follower_count = Column(Integer)

    tag_id = Column(ForeignKey("tag.id"))

    tags = relationship("Tag", back_populates="games")
    videos = relationship("Video", back_populates="game")


class Tag(Base):
    __tablename__ = "tag"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, onupdate=func.now())
    is_auto = Column(Boolean)  # true if auto-generated
    localization_names = Column(JSON)
    localization_discription = Column(JSON)

    streams = relationship("Stream", secondary=StreamTag, back_populates="tags")
    games = relationship("Game", secondary=GameTag, back_populates="tags")


class Chat(Base):
    __tablename__ = "chat"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, onupdate=func.now())
    type = Column(String)  # exp. for_followers_only

    top_gifter_id = Column(ForeignKey("user.id"))
    emoji_id = Column(ForeignKey("emoji.id"))

    stream = relationship("Stream", back_populates="chat", uselist=False)
    top_gifters = relationship("User", secondary=ChatGifters, back_populates="chats")
    emojis = relationship("Emoji", secondary=ChatEmojis, back_populates="chats")
    messages = relationship("Message", back_populates="chat")
    video = relationship("Video", back_populates="chat", uselist=False)


class Emoji(Base):
    __tablename__ = "emoji"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, onupdate=func.now())
    image_url = Column(String)
    name = Column(String)
    type = Column(String)  # global, sub emote, ?unbloked?

    chats = relationship("Chat", secondary=ChatEmojis, back_populates="emojis")


class Message(Base):
    __tablename__ = "message"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, onupdate=func.now())
    text = Column(String)
    sent_at = Column(Integer)
    user_role = Column(String)  # moderator, GLHF Pledge, ...

    chat_id = Column(ForeignKey("chat.id"))
    user_id = Column(ForeignKey("user.id"))

    chat = relationship("Chat", back_populates="messages")
    user = relationship("User", back_populates="messages")

engine = create_engine(f'postgresql://{POSTGRES_LOGIN}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRESS_DB}')

if __name__ == "__main__":
    Base.metadata.create_all(engine)
