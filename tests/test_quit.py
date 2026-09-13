"""Global Quit option behavior tests."""

import pytest

from src import utils


class Selection:
    def ask(self):
        return utils.QUIT_VALUE


def test_select_with_quit_adds_red_choice_and_raises(monkeypatch) -> None:
    captured = {}

    def select(message, choices, default=None):
        captured["choices"] = choices
        return Selection()

    monkeypatch.setattr(utils.questionary, "select", select)
    with pytest.raises(utils.QuitRequested):
        utils.select_with_quit("Select a category", ["Animals"])

    quit_option = captured["choices"][-1]
    assert quit_option.value is utils.QUIT_VALUE
    assert quit_option.title == [("fg:#ff0000 bold", "Quit")]


def test_confirm_with_quit_uses_yes_no_choices(monkeypatch) -> None:
    captured = {}

    def select_with_quit(message, choices, default=None):
        captured.update(message=message, choices=choices, default=default)
        return True

    monkeypatch.setattr(utils, "select_with_quit", select_with_quit)
    assert utils.confirm_with_quit("Add another text?", default=False) is True
    assert [choice.title for choice in captured["choices"]] == ["Yes", "No"]
    assert captured["default"] is False
