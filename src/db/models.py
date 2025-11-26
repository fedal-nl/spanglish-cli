from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .base import Base
from src.enums import CategoryEnum

class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False)
    category = Column(Enum(CategoryEnum), nullable=False)
    translation = Column(String, nullable=False)

    verb = relationship("Verb", back_populates="word", uselist=False)

class Verb(Base):
    __tablename__ = "verbs"

    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)

    yo = Column(String)
    tu = Column(String)
    ella_el = Column(String)
    nosotros = Column(String)
    vosotros = Column(String)
    ellos_ellas = Column(String)

    word = relationship("Word", back_populates="verb")
