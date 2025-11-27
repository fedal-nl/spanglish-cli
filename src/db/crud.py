from .models import Word, Verb, Translation
from sqlalchemy.orm import selectinload
from .base import get_session

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

def list_words(category: str = None):
    with get_session() as session:
        query = (
            session.query(Word).options(selectinload(Word.translations))
        )
        if category:
            query = query.filter(Word.category == category)
        rows = query.order_by(Word.word).all()
        return rows

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
