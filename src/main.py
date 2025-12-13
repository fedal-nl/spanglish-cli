# main.py
import typer
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import RadioList
from prompt_toolkit.styles import Style

from src.dictionary.commands.vocabulary import app as dictionary_app
from src.dictionary.commands.quizes import app as quiz_app

app = typer.Typer(add_completion=False)

# ======== Styles ========
style = Style.from_dict({
    "header": "bg:#000000 #88c0d0 bold",
    "body": "bg:#000000 #d8dee9",
    "footer": "bg:#000000 #a3be8c",
    "radiolist": "bg:#000000 #d8dee9",
    "radiolist focused": "bg:#81a1c1 #2e3440 bold",
    "": "bg:#000000 #ffffff",  # base background to remove grey
})

# ======== Header Text ========
HEADER_TEXT = """\
SPANGISH — Spanish Vocabulary Trainer
Learn Spanish interactively from your terminal!
"""

FOOTER_TEXT = "Use ↑↓ to navigate, Enter to select, Esc to quit."


# ======== Menu options ========
MENU_OPTIONS = [
    ("add", "Add text to dictionary"),
    ("list", "List vocabulary"),
    ("quiz", "Start quiz"),
]

# ======== Key bindings ========
kb = KeyBindings()

@kb.add("escape")
def _(event):
    event.app.exit(result=None)


def spanglish_menu():
    """
    Show the main menu with header, footer, and centered RadioList.
    Returns: the selected value or None if Escape pressed
    """
    radio_list = RadioList(MENU_OPTIONS)

    # Layout: header / menu / footer
    layout = Layout(
        HSplit([
            Window(
                content=FormattedTextControl(HEADER_TEXT),
                height=HEADER_TEXT.count("\n") + 1,
                style="class:header",
                dont_extend_width=True,
            ),
            Window(height=1, char="-", style="class:body"),  # separator
            VSplit([
                Window(),  # left spacer
                radio_list,
                Window(),  # right spacer
            ], height=len(MENU_OPTIONS)+2),
            Window(height=1, char="-", style="class:body"),  # separator
            Window(
                content=FormattedTextControl(FOOTER_TEXT),
                height=1,
                style="class:footer",
                dont_extend_width=True,
            ),
        ])
    )

    app_tui = Application(
        layout=layout,
        key_bindings=kb,
        style=style,
        full_screen=True,
    )

    # Focus the RadioList so Enter works
    app_tui.layout.focus(radio_list)

    return app_tui.run()


# ======== Typer callback ========
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        choice = spanglish_menu()

        if choice is None:
            raise typer.Exit()

        if choice == "add":
            ctx.invoke(dictionary_app.get_command("add"))
        elif choice == "list":
            ctx.invoke(dictionary_app.get_command("list"))
        elif choice == "quiz":
            ctx.invoke(quiz_app.get_command("start"))

        raise typer.Exit()


# ======== Add Typer subcommands for CLI fallback ========
app.add_typer(dictionary_app, name="dictionary", help="Manage vocabulary")
app.add_typer(quiz_app, name="quiz", help="Start quizzes")

# ======== Entry point ========
if __name__ == "__main__":
    app()
