import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from src.commands.quizes import app as quiz_app
from src.commands.words import app as words_app

console = Console()

app = typer.Typer(
    add_completion=False,  # optional
    help="Spanglish — Spanish Vocabulary Trainer CLI"
)


def print_header():
    """Pretty ASCII banner for SPANGLISH."""
    banner = Text(r"""
   ███████╗██████╗  █████╗ ███╗   ██╗ ██████╗ ██╗     ██╗███████╗██╗.   ██╗
   ██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔════╝ ██║     ██║██╔════╝██║.   ██║
   ███████╗██████╔╝███████║██╔██╗ ██║██║  ███╗██║     ██║███████╗█████████║
   ╚════██║██╔══.  ██╔══██║██║╚██╗██║██║   ██║██║     ██║╚════██║██║.   ██║
   ███████║██║     ██║  ██║██║ ╚████║╚██████╔╝███████╗██║███████║██║.   ██║
   ╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝╚══════╝╚═╝.   ╚═╝
                      📘 SPANGLISH CLI
""", style="bold cyan")

    console.print(banner)

    console.print(
        Panel.fit(
            "[bold yellow]🇪🇸🇺🇸  Spanglish — Spanish Vocabulary Trainer[/bold yellow]\n"
            "[white]Learn Spanish interactively from your terminal![/white]\n\n"
            "• 🔤 Practice words with smart quizzes\n"
            "• 📚 Manage your personalized vocabulary list\n"
            "• 📈 Track progress over multiple sessions\n",
            border_style="cyan",
            padding=(1, 2)
        )
    )


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    """Show the full header + help when no command is used."""
    if ctx.invoked_subcommand is None:
        print_header()
        typer.echo(ctx.get_help())


# Add subcommands with styled help
app.add_typer(
    quiz_app,
    name="quiz",
    help="🎯 Quiz commands: start quizzes and view performance."
)

app.add_typer(
    words_app,
    name="words",
    help="📚 Word commands: list, add, and manage vocabulary."
)


if __name__ == "__main__":
    app()
