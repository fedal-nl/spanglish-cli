from .models import Word, Verb, Translation, Quiz
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from .base import get_session
from src.enums import CategoryEnum

def create_word(word: str, category: str, translations: list[str]):
    with get_session() as session:
        w = Word(word=word, category=category)
        session.add(w)
        session.flush()

        for t in translations:
            tr = Translation(word=w, translation=t)
            session.add(tr)
        
        session.commit()
        session.refresh(w)
        return w


def list_words(category: CategoryEnum = None, limit: int = None, is_random: bool = False):
    with get_session() as session:
        query = (
            session.query(Word).options(selectinload(Word.translations))
        )
        if category:
            query = query.filter(Word.category == category)

        if limit:
            query = query.limit(limit)

        if is_random:
            return query.order_by(func.random()).all()
        else:
            return query.order_by(Word.word).all()


def create_verb(word_id: int, yo, tu, ella_el, nosotros, vosotros, ellos_ellas):
    with get_session() as session:
        v = Verb(
            word_id=word_id,
            yo=yo,
            tu=tu,
            ella_el=ella_el,
            nosotros=nosotros,
            vosotros=vosotros,
            ellos_ellas=ellos_ellas
        )
        session.add(v)
        session.commit()
        return v


def list_verbs():
    with get_session() as session:
        return (
            session.query(Verb).options(selectinload(Verb.word))
            .join(Word)
            .order_by(Word.word)
            .all()
        )


def create_quiz(word_id: int, is_correct: bool):
    with get_session() as session:
        quiz = Quiz(word_id=word_id, is_correct=is_correct)
        session.add()
        session.commit()
        return quiz


def list_quizes():
    with get_session() as session:
        return (
            session.query(Quiz).options(selectinload(Quiz.word))
            .join(Word)
            .order_by(Quiz.created_at.desc())
            .all()
        )
