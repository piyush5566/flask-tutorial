from .db import db
import typing as t
from datetime import datetime
from flask_security.models import fsqla_v3 as fsqla
from sqlalchemy import Column, ForeignKey, Integer, Text, UnicodeText

fsqla.FsModels.set_db_info(db)


class User(db.Model, fsqla.FsUserMixin):
    __tablename__ = "user"
    posts: db.Mapped[t.List["Post"]] = db.relationship(
        "Post", back_populates="user", lazy="dynamic", cascade_backrefs=False
    )


class Role(db.Model, fsqla.FsRoleMixin):
    __tablename__ = "role"


class Post(db.Model):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created: db.Mapped[datetime] = db.mapped_column(default=datetime.now)
    user: db.Mapped["User"] = db.relationship(
        "User", back_populates="posts", cascade_backrefs=False
    )
    title = Column(Text)
    body = Column(UnicodeText)
