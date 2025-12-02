from sqlalchemy import func
from sqlalchemy.orm import selectinload

from src.enums import CategoryEnum

from .base import get_session
from .models import QuizAttempt, QuizSession, Translation, Verb, Word


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


def list_words(category: CategoryEnum=None, limit: int=None, is_random: bool=False):
    with get_session() as session:
        query = (
            session.query(Word)
            .options(selectinload(Word.translations))
            .options(selectinload(Word.verb))
        )

        if category is not None:
            query = query.filter(Word.category == category)

        query = query.order_by(func.random() if is_random else Word.word)

        if limit is not None:
            query = query.limit(limit)

        return query.all()


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


def create_quiz_session():
    with get_session() as session:
        quiz_session = QuizSession()
        session.add(quiz_session)
        session.commit()
        return quiz_session


def create_quiz_attempt(session_id: int, word_id: int, answered_correctly: bool):
    with get_session() as session:
        quiz_attempt = QuizAttempt(
            session_id=session_id,
            word_id=word_id,
            answered_correctly=answered_correctly
        )
        session.add(quiz_attempt)
        session.commit()
        return quiz_attempt


# def list_quizes():
#     with get_session() as session:
#         return (
#             session.query(QuizAttempt)
#             .options(selectinload(QuizAttempt.word))
#             .join(Word)
#             .order_by(QuizAttempt.created_at.desc())
#             .all()
#         )
