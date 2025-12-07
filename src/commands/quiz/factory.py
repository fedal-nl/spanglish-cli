"""Responsable for converting DB models to Quiz models."""
from src.commands.quiz.models import QuizItem
from src.db.models import Sentence, Word
from src.enums import LanguageEnum, QuizContentTypeEnum


def convert_word_to_quiz_item(word: Word, quiz_language: LanguageEnum) -> QuizItem:
    """Convert a Word DB model to a QuizItem."""
    verb = word.verb
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
        question = word.word
        answer = ", ".join([t.translation for t in word.translations])
    else:
        question = ", ".join([t.translation for t in word.translations])
        answer = word.word

    return QuizItem(
        content_type_id=word.id,
        content_type=QuizContentTypeEnum.WORD,
        question=question,
        answer=answer,
        # For verbs, include conjugations
        conjugation=conjugation,
        category=word.category,
    )


def convert_sentence_to_quiz_item(
        sentence: Sentence,
        quiz_language: LanguageEnum
    ) -> QuizItem:
    """Convert a Sentence DB model to a QuizItem. Based on quiz language."""
    if quiz_language == LanguageEnum.SPANISH:
        return QuizItem(
            content_type_id=sentence.id,
            content_type=QuizContentTypeEnum.SENTENCE,
            question=sentence.spanish,
            answer=sentence.english,
            category=sentence.topic,
        )
    return QuizItem(
        content_type_id=sentence.id,
        content_type=QuizContentTypeEnum.SENTENCE,
        question=sentence.english,
        answer=sentence.spanish,
        category=sentence.topic,
    )
