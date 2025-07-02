from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship


db = SQLAlchemy()

book_subjects = Table(
    "book_subjects",
    db.Model.metadata,
    db.Column("book_id", Integer, ForeignKey("books.id"),primary_key=True),
    db.Column("subject_id", Integer,ForeignKey("subjects.id"),primary_key=True)
)
class UserBook(db.Model):
    __tablename__ = "user_books"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),primary_key=True)
    book_id:Mapped[int] = mapped_column(ForeignKey("books.id"), primary_key=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_recommended: Mapped[bool] = mapped_column(Boolean, default=True)

    user = relationship("User", back_populates="user_books")
    book = relationship("Book", back_populates="user_books")

class User(UserMixin,db.Model):
    __tablename__= "users"
    id:Mapped[int] = mapped_column(primary_key=True)
    email:Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    name:Mapped[str] = mapped_column(String(150), nullable=False)
    password:Mapped[str] = mapped_column(String(250), nullable=False)

    user_books = relationship("UserBook", back_populates="user", cascade="all, delete-orphan")

class Book(db.Model):
    __tablename__ = "books"
    id:Mapped[int] = mapped_column(primary_key=True)
    title:Mapped[str] = mapped_column(String(250), nullable=False)
    author:Mapped[str] = mapped_column(String(250), nullable=False)
    link:Mapped[str] = mapped_column(String(250), nullable=False)

    user_books = relationship("UserBook", back_populates="book", cascade="all, delete-orphan")
    subjects = relationship("Subject", secondary=book_subjects, back_populates="books")

class Subject(db.Model):
    __tablename__ = "subjects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    is_recommended: Mapped[bool] = mapped_column(Boolean, default=True)

    books = relationship("Book", secondary=book_subjects, back_populates="subjects")


