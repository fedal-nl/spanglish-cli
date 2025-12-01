import typer

from src.commands.quizes import app as quiz_app
from src.commands.words import app as words_app

app = typer.Typer()
app.add_typer(quiz_app, name="quiz")
app.add_typer(words_app, name="words")

if __name__ == "__main__":
    app()
