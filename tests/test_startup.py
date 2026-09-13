"""Startup connection and authentication preflight tests."""

from types import SimpleNamespace

from src.api_client import SpanglishAPIError
from src.dictionary_app import __main__ as application


def client(**overrides):
    values = {
        "check_connection": lambda: None,
        "check_authentication": lambda: "learner@example.com",
        "login": lambda email, password: email,
        "register": lambda username, email, password: email,
        "request_password_reset": lambda email: None,
        "confirm_password_reset": lambda token, password: None,
        "close": lambda: None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def fail(message: str):
    def operation():
        raise SpanglishAPIError(message)

    return operation


def test_startup_checks_succeed(capsys) -> None:
    assert application.startup_checks(client()) is True
    output = capsys.readouterr().out
    assert "Checking connection ... success" in output
    assert "Checking authentication ... success (learner@example.com)" in output


def test_startup_stops_after_connection_error(capsys) -> None:
    auth_calls = []
    subject = client(
        check_connection=fail("API offline"),
        check_authentication=lambda: auth_calls.append(True),
    )
    assert application.startup_checks(subject) is False
    assert auth_calls == []
    assert "Checking connection ... error" in capsys.readouterr().out


def test_startup_prompts_for_login_after_authentication_error(
    monkeypatch, capsys
) -> None:
    login_calls = []
    subject = client(
        check_authentication=fail("Not logged in"),
        login=lambda email, password: login_calls.append((email, password)) or email,
    )
    monkeypatch.setattr(application, "choice", lambda **_kwargs: "login")
    monkeypatch.setattr("builtins.input", lambda _message: "learner@example.com")
    monkeypatch.setattr(application.getpass, "getpass", lambda _message: "secret")
    assert application.startup_checks(subject) is True
    output = capsys.readouterr().out
    assert "Checking connection ... success" in output
    assert "Checking authentication ... error" in output
    assert "Not logged in" not in output
    assert "Authentication ... success (learner@example.com)" in output
    assert login_calls == [("learner@example.com", "secret")]


def test_startup_stops_when_login_fails(monkeypatch, capsys) -> None:
    def invalid_login(_email, _password):
        raise SpanglishAPIError("Invalid credentials")

    subject = client(
        check_authentication=fail("Not logged in"), login=invalid_login
    )
    monkeypatch.setattr(application, "choice", lambda **_kwargs: "login")
    monkeypatch.setattr("builtins.input", lambda _message: "learner@example.com")
    monkeypatch.setattr(application.getpass, "getpass", lambda _message: "wrong")
    assert application.startup_checks(subject) is False
    assert "Authentication failed: Invalid credentials" in capsys.readouterr().out


def test_startup_can_signup_and_login(monkeypatch, capsys) -> None:
    calls = []
    subject = client(
        check_authentication=fail("Not logged in"),
        register=lambda username, email, password: calls.append(
            ("register", username, email, password)
        ) or email,
        login=lambda email, password: calls.append(("login", email, password))
        or email,
    )
    answers = iter(["learner@example.com", "learner"])
    passwords = iter(["secret-password", "secret-password"])
    monkeypatch.setattr(application, "choice", lambda **_kwargs: "signup")
    monkeypatch.setattr("builtins.input", lambda _message: next(answers))
    monkeypatch.setattr(
        application.getpass, "getpass", lambda _message: next(passwords)
    )

    assert application.startup_checks(subject) is True
    assert calls == [
        ("register", "learner", "learner@example.com", "secret-password"),
        ("login", "learner@example.com", "secret-password"),
    ]
    assert "Account created. Logging in" in capsys.readouterr().out


def test_startup_can_exit_authentication(monkeypatch, capsys) -> None:
    subject = client(check_authentication=fail("Not logged in"))
    monkeypatch.setattr(application, "choice", lambda **_kwargs: "quit")
    assert application.startup_checks(subject) is False
    assert "Authentication cancelled" in capsys.readouterr().out


def test_keyboard_interrupt_exits_without_traceback(monkeypatch, capsys) -> None:
    def interrupted():
        raise KeyboardInterrupt

    monkeypatch.setattr(application, "main_menu", interrupted)
    application.run()
    assert "Exiting Spanglish CLI. Goodbye!" in capsys.readouterr().out


def test_startup_can_reset_password_and_login(monkeypatch, capsys) -> None:
    calls = []
    subject = client(
        check_authentication=fail("Not logged in"),
        request_password_reset=lambda email: calls.append(("request", email)),
        confirm_password_reset=lambda token, password: calls.append(
            ("confirm", token, password)
        ),
        login=lambda email, password: calls.append(("login", email, password))
        or email,
    )
    answers = iter(["learner@example.com", "reset-token-value-that-is-long-enough"])
    passwords = iter(["new-password", "new-password"])
    monkeypatch.setattr(application, "choice", lambda **_kwargs: "reset")
    monkeypatch.setattr("builtins.input", lambda _message: next(answers))
    monkeypatch.setattr(
        application.getpass, "getpass", lambda _message: next(passwords)
    )

    assert application.startup_checks(subject) is True
    assert calls == [
        ("request", "learner@example.com"),
        ("confirm", "reset-token-value-that-is-long-enough", "new-password"),
        ("login", "learner@example.com", "new-password"),
    ]
    assert "Password reset. Authenticated" in capsys.readouterr().out
