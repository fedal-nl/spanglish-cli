from .models import Word, Verb
from .base import get_session

def create_word(word: str, category: str, translation: str):
    with get_session() as session:
        w = Word(word=word, category=category, translation=translation)
        session.add(w)
        session.commit()
        session.refresh(w)
        return w

def list_words(category: str = None):
    with get_session() as session:
        query = session.query(Word)
        if category:
            query = query.filter(Word.category == category)
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
            session.query(Verb)
            .join(Word)
            .order_by(Word.word)
            .all()
        )
