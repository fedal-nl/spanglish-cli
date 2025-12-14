"""Responsable for converting DB models to Quiz models."""
from src.db.models import Dictionary
from src.dictionary_app.commands.quiz.models import QuizItem
from src.enums import LanguageEnum


def convert_dictionary_to_quiz_item(
        dictionary: Dictionary,
        quiz_language: LanguageEnum
    ) -> QuizItem:
    """Convert a Dictionary DB model to a QuizItem based on content type."""
    verb = dictionary.verb
    conjugation = None
    # If the word has a verb conjugation, include it
    if verb:
        conjugation = {
            "yo": verb.yo,
            "tú": verb.tu,
            "él/ella": verb.ella_el,
            "nosotros": verb.nosotros,
            "vosotros": verb.vosotros,
            "ellos/ellas": verb.ellos_ellas,
        }
    # Depending on quiz language, set question and answer
    if quiz_language == LanguageEnum.SPANISH:
        question = dictionary.text
        answer = ", ".join([t.translation for t in dictionary.translations])
    else:
        question = ", ".join([t.translation for t in dictionary.translations])
        answer = dictionary.text
    return QuizItem(
        text_id=dictionary.id,
        question=question,
        answer=answer,
        # For verbs, include conjugations
        conjugation=conjugation,
        category=dictionary.category,
    )
