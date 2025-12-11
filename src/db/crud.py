from sqlalchemy import func
from sqlalchemy.orm import selectinload

from src.enums import CategoryEnum

from .base import get_session
from .models import Dictionary, QuizAttempt, QuizSession, Translation, Verb


# Crud operations for the Dictionary app
def add_text_to_dictionary(
        text: str,
        category: CategoryEnum,
        translations: list[str]
    ):
    with get_session() as session:
        dict_entry = Dictionary(
            text=text,
            category=category,
        )
        session.add(dict_entry)
        session.flush()  # To get the ID

        for t in translations:
            tr = Translation(dictionary_id=dict_entry.id, translation=t)
            session.add(tr)

        session.commit()
        session.refresh(dict_entry)
        return dict_entry


def list_dictionary_entries(
        category: CategoryEnum|None=None,
        limit: int=None,
        is_random: bool=False
    ):
    with get_session() as session:
        query = (
            session.query(Dictionary)
            .options(selectinload(Dictionary.translations))
            .options(selectinload(Dictionary.verb))
        )

        if category:
            print(f"Applying filter for category: {category}")
            query = query.filter(Dictionary.category == category)

        query = query.order_by(func.random() if is_random else Dictionary.text)

        if limit is not None:
            query = query.limit(limit)

        return query.all()


def create_verb(dictionary_id: int, yo, tu, ella_el, nosotros, vosotros, ellos_ellas):
    with get_session() as session:
        v = Verb(
            dictionary_id=dictionary_id,
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
            session.query(Verb).options(selectinload(Verb.dictionary))
            .join(Dictionary)
            .order_by(Dictionary.text)
            .all()
        )


def create_quiz_session():
    with get_session() as session:
        quiz_session = QuizSession()
        session.add(quiz_session)
        session.commit()
        return quiz_session


def create_quiz_attempt(
        session_id: int,
        dictionary_id: int,
        answer: str,
        answered_correctly: bool
    ):
    with get_session() as session:
        quiz_attempt = QuizAttempt(
            session_id=session_id,
            dictionary_id=dictionary_id,
            answer=answer,
            answered_correctly=answered_correctly
        )
        session.add(quiz_attempt)
        session.commit()
        session.refresh(quiz_attempt)
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
