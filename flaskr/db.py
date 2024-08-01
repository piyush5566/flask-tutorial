from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(String(128))
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="user")


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    created: Mapped[datetime] = mapped_column(default=datetime.now)
    title: Mapped[str]
    body: Mapped[str]

    user: Mapped["User"] = relationship("User", back_populates="posts")


def init_app(app):
    """Register database functions with the Flask app. This is called by the application factory."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
