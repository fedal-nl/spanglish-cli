import typer
from prompt_toolkit.shortcuts import choice
from prompt_toolkit.styles import Style
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from src.dictionary.commands.quizes import start
from src.dictionary.commands.vocabulary import add
from src.dictionary.commands.vocabulary import list as list_vocabulary

console = Console()

app = typer.Typer(
    add_completion=False,  # optional
    help="Spanglish — Spanish Vocabulary Trainer CLI"
)

style = Style.from_dict({
    "radiolist": "bg:#000000",
    "radiolist focused": "bg:#81a1c1 #2e3440 bold",
    "": "bg:#000000 #ffffff",  # base background to remove grey
})


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

    console.print(Align.center(banner))

    console.print(
        Align.center(
            Panel.fit(
                "[bold yellow]Spanglish — Spanish/English Vocabulary Trainer[/bold yellow]\n"
                "[white]Learn Spanish interactively from your terminal![/white]\n\n"
                "• 🔤 Practice words with smart quizzes\n"
                "• 📚 Manage your personalized vocabulary list\n"
                "• 📈 Track progress over multiple sessions\n",
                border_style="cyan",
                padding=(1, 2)
            )
        )
    )


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    """Show the full header + help when no command is used."""
    if ctx.invoked_subcommand is None:
        print_header()
        typer.echo(ctx.get_help())

        selected_choice = choice(
            message="Select an option?",
            options=[
                (1, "Start Quiz"),
                (2, "Add Vocabulary"),
                (3, "List Vocabulary"),
                (4, "Exit")
            ],
            default=1,
            style=style
        )

        print(f"Selected Value => {selected_choice}")
        if selected_choice == 1:
            ctx.invoke(start)
        elif selected_choice == 2:
            ctx.invoke(add)
        elif selected_choice == 3:
            ctx.invoke(list_vocabulary)
        else:
            console.print("\n[bold red]Exiting Spanglish CLI. Goodbye![/bold red]\n")
            raise typer.Exit()


if __name__ == "__main__":
    app()
"""Entry point for the dictionary module."""
