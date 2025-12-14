import sys

from prompt_toolkit.shortcuts import choice
from prompt_toolkit.styles import Style
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

# Import your command functions directly
from src.dictionary_app.commands.quizes import start
from src.dictionary_app.commands.vocabulary import add
from src.dictionary_app.commands.vocabulary import list as list_vocabulary

console = Console()

style = Style.from_dict({
    "radiolist": "bg:#000000",
    "radiolist focused": "bg:#81a1c1 #2e3440 bold",
    "": "bg:#000000 #ffffff",  # base background to remove grey
})


def print_header():
    """Pretty ASCII banner for SPANGLISH."""
    # ... (header printing logic remains the same) ...
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

def main_menu():
    """
    Main application loop driven entirely by prompt_toolkit choices.
    """
    # Print the header once at startup
    print_header()

    while True: # Keep showing the menu until user exits
        # print("\n" + "="*50 + "\n") # Separator for clarity in loop
        console.print(Rule(style="cyan"))

        selected_choice = choice(
            message="Select an option:",
            options=[
                ("1", "Start Quiz"),
                ("2", "Add Vocabulary"),
                ("3", "List Vocabulary"),
                ("4", "Exit")
            ],
            default="1",
            style=style
        )

        if selected_choice == "1":
            start()
        elif selected_choice == "2":
            add()
        elif selected_choice == "3":
            list_vocabulary()
        elif selected_choice == "4":
            console.print("\n[bold red]Exiting Spanglish CLI. Goodbye![/bold red]\n")
            sys.exit(0) # Exit the script cleanly
        else:
            # Should not happen with prompt_toolkit choice, but good practice
            console.print("[bold red]Invalid selection, please try again.[/bold red]")


if __name__ == "__main__":
    # Start the interactive main menu function directly
    main_menu()
