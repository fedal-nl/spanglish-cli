"""This module contains functions that provide quiz questions and answers.
Using the prompt_toolkit library for enhanced user interaction.
"""
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import prompt

from src.enums import LanguageEnum

from .models import QuizItem
from .scores import get_score


def ask_question(item: QuizItem, language: LanguageEnum) -> tuple[str, bool]:
    """Ask a quiz question to the user and get their answer.

    Args:
        item (QuizItem): The quiz item containing question and answer.
        language (LanguageEnum): The language of the quiz.

    Returns:
        tuple: A tuple containing the user's answer and whether it was correct.
    """

    if language == LanguageEnum.SPANISH:
        prompt_text = HTML(
            f"What is the translation of {item.question} ? "
        )
    else:
        prompt_text = HTML(
            f"What is the translation of {item.question} in {language.name} ? "
        )

    user_answer = prompt(prompt_text)

    is_correct = get_score(item.answer, user_answer or "")
    # If the answer is correct and the item has verb conjugations, ask for them as well
    if is_correct and item.conjugation:
        verb_answer, verb_correct = ask_verb_conjugation(item)
        if verb_answer:
            user_answer += f" | Verb Conjugation: {verb_answer}"
        is_correct = is_correct and verb_correct

    return user_answer or "", is_correct

def ask_verb_conjugation(item: QuizItem) -> tuple[str, bool]:
    """Ask the user to conjugate a verb and get their answers.

    Args:
        item (QuizItem): The quiz item containing verb conjugations.
    Returns:
        tuple: A tuple with user answer and correctness for the conjugation.
    """
    if item.conjugation:
        for pronoun, correct_form in item.conjugation.items():
            user_answer = prompt(f"Conjugate for '{pronoun}': ")
            is_correct = get_score(correct_form, user_answer or "")
            # if there is a wrong answer, return immediately
            if not is_correct:
                return user_answer, is_correct
    return "", True
