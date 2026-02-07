from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.enums import CategoryEnum

from .base import Base


class Translation(Base):
    __tablename__ = "translations"

    id: Mapped[int] = mapped_column(primary_key=True)
    dictionary_id: Mapped[int] = mapped_column(ForeignKey(
        "dictionary.id",
        name="fk_translation_dictionary_id_dictionary"
        ), nullable=False)
    translation: Mapped[str] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint("dictionary_id", "translation"),
    )

    dictionary = relationship("Dictionary", back_populates="translations")

class Verb(Base):
    __tablename__ = "verbs"

    id: Mapped[int] = mapped_column(primary_key=True)
    dictionary_id: Mapped[int] = mapped_column(ForeignKey(
        "dictionary.id",
        name="fk_verb_dictionary_id_dictionary"
    ), nullable=False, unique=True)
    yo: Mapped[str] = mapped_column(String)
    tu: Mapped[str] = mapped_column(String)
    ella_el: Mapped[str] = mapped_column(String)
    nosotros: Mapped[str] = mapped_column(String)
    vosotros: Mapped[str] = mapped_column(String)
    ellos_ellas: Mapped[str] = mapped_column(String)

    dictionary = relationship("Dictionary", back_populates="verb")


class Dictionary(Base):
    __tablename__ = "dictionary"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False, index=True)
    category: Mapped[CategoryEnum] = mapped_column(
        Enum(
            CategoryEnum, name="mergedcategory", native_enum=True, create_type=False
        ), nullable=False, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, index=True
    )
    # Relationship to verbs
    verb: Mapped["Verb"] = relationship(
        "Verb", back_populates="dictionary", uselist=False
    )
    # Relationship to translations
    translations: Mapped[list["Translation"]]  = relationship(
        "Translation",
        back_populates="dictionary",
        cascade="all, delete-orphan"
    )

    # create constraints to ensure word uniqueness
    __table_args__ = (
        UniqueConstraint("text", "category"),
    )

class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, index=True)

    attempts = relationship(
        "QuizAttempt",
        back_populates="session",
        cascade="all, delete-orphan"
    )

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)

    # foreign key to dictionary table
    dictionary_id: Mapped[int] = mapped_column(ForeignKey(
        "dictionary.id",
        name="fk_quizattempt_dictionary_id_dictionary"
    ), nullable=False)
    answer: Mapped[str] = mapped_column(String, nullable=False)
    # whether the answer was correct or not, for statistics
    answered_correctly: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, index=True
    )
    session_id: Mapped[int] = mapped_column(ForeignKey(
        "quiz_sessions.id",
        name="fk_quizattempt_session_id_quizsessions"
    ), nullable=False)

    session = relationship("QuizSession", back_populates="attempts")
