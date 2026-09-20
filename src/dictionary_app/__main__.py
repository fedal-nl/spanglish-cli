import getpass
import sys

from prompt_toolkit.shortcuts import choice
from prompt_toolkit.styles import Style
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

from src.api_client import SpanglishAPIClient, SpanglishAPIError
from src.dictionary_app.commands.quizes import start
from src.dictionary_app.commands.vocabulary import (
    add_vocabulary,
    create_category,
    create_chapter,
    delete_vocabulary,
    list_vocabulary,
    update_vocabulary,
)
from src.utils import QuitRequested

console = Console()

style = Style.from_dict(
    {
        "radiolist": "bg:#000000",
        "radiolist focused": "bg:#81a1c1 #2e3440 bold",
        "": "bg:#000000 #ffffff",  # base background to remove grey
    }
)


def print_header():
    """Pretty ASCII banner for SPANGLISH."""
    # ... (header printing logic remains the same) ...
    banner = Text(
        r"""
   ███████╗██████╗  █████╗ ███╗   ██╗ ██████╗ ██╗     ██╗███████╗██╗.   ██╗
   ██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔════╝ ██║     ██║██╔════╝██║.   ██║
   ███████╗██████╔╝███████║██╔██╗ ██║██║  ███╗██║     ██║███████╗█████████║
   ╚════██║██╔══.  ██╔══██║██║╚██╗██║██║   ██║██║     ██║╚════██║██║.   ██║
   ███████║██║     ██║  ██║██║ ╚████║╚██████╔╝███████╗██║███████║██║.   ██║
   ╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝╚══════╝╚═╝.   ╚═╝
                      📘 SPANGLISH CLI
""",
        style="bold cyan",
    )

    console.print(Align.center(banner))

    console.print(
        Align.center(
            Panel.fit(
                "[bold yellow]Spanglish — Spanish/English "
                "Vocabulary Trainer[/bold yellow]\n"
                "[white]Learn Spanish interactively from your terminal![/white]\n\n"
                "• 🔤 Practice words with smart quizzes\n"
                "• 📚 Manage your personalized vocabulary list\n"
                "• 📈 Track progress over multiple sessions\n",
                border_style="cyan",
                padding=(1, 2),
            )
        )
    )


def main_menu():  # noqa: C901
    """
    Main application loop driven entirely by prompt_toolkit choices.
    """
    if not startup_checks():
        return

    # Print the header once at startup
    print_header()

    while True:  # Keep showing the menu until user exits
        # print("\n" + "="*50 + "\n") # Separator for clarity in loop
        console.print(Rule(style="cyan"))

        selected_choice = choice(
            message="Select an option:",
            options=[
                ("1", "Add Vocabulary"),
                ("2", "List Vocabulary"),
                ("3", "Update Vocabulary"),
                ("4", "Delete Vocabulary"),
                ("5", "Start Quiz"),
                ("6", "Create Category"),
                ("7", "Create Chapter"),
                ("8", [("fg:#ff0000 bold", "Quit")]),
            ],
            default="1",
            style=style,
        )

        if selected_choice == "1":
            add_vocabulary()
        elif selected_choice == "2":
            list_vocabulary()
        elif selected_choice == "3":
            update_vocabulary()
        elif selected_choice == "4":
            delete_vocabulary()
        elif selected_choice == "5":
            start()
        elif selected_choice == "6":
            create_category()
        elif selected_choice == "7":
            create_chapter()
        elif selected_choice == "8":
            console.print("\n[bold red]Exiting Spanglish CLI. Goodbye![/bold red]\n")
            sys.exit(0)  # Exit the script cleanly
        else:
            # Should not happen with prompt_toolkit choice, but good practice
            console.print("[bold red]Invalid selection, please try again.[/bold red]")


def startup_checks(client: SpanglishAPIClient | None = None) -> bool:
    """Require a healthy API and valid saved session before showing the menu."""
    owns_client = client is None
    client = client or SpanglishAPIClient()
    try:
        console.print("Checking connection ... ", end="")
        try:
            client.check_connection()
        except SpanglishAPIError as exc:
            console.print("[red]error[/red]")
            console.print(f"[red]{exc}[/red]")
            return False
        console.print("[green]success[/green]")
        console.print("Checking authentication ... ", end="")
        try:
            identity = client.check_authentication()
        except SpanglishAPIError:
            console.print("[red]error[/red]")
            return authenticate_interactively(client)
        console.print(f"[green]success[/green] ({identity})")
        return True
    finally:
        if owns_client:
            client.close()


def authenticate_interactively(client: SpanglishAPIClient) -> bool:
    """Offer login or account creation when no valid session is available."""
    action = choice(
        message="Authentication required:",
        options=[
            ("login", "Login"),
            ("signup", "Sign up"),
            ("reset", "Forgot password"),
            ("quit", [("fg:#ff0000 bold", "Quit")]),
        ],
        default="login",
        style=style,
    )
    if action == "quit":
        console.print("Authentication cancelled.")
        return False

    if action == "reset":
        return reset_password_interactively(client)

    email = input("Email: ").strip()
    if action == "signup":
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        confirmation = getpass.getpass("Confirm password: ")
        if password != confirmation:
            console.print("[red]Passwords do not match.[/red]")
            return False
        try:
            client.register(username, email, password)
        except SpanglishAPIError as signup_error:
            console.print(f"[red]Sign-up failed: {signup_error}[/red]")
            return False
        console.print("Account created. Logging in ...")
    else:
        password = getpass.getpass("Password: ")

    try:
        identity = client.login(email, password)
    except SpanglishAPIError as login_error:
        console.print(f"[red]Authentication failed: {login_error}[/red]")
        return False
    console.print(f"Authentication ... [green]success[/green] ({identity})")
    return True


def reset_password_interactively(client: SpanglishAPIClient) -> bool:
    """Request a reset token, set a new password, and log the user in."""
    email = input("Account email: ").strip()
    try:
        client.request_password_reset(email)
    except SpanglishAPIError as request_error:
        console.print(f"[red]Password reset request failed: {request_error}[/red]")
        return False
    console.print(
        "If the account exists, a reset token has been sent to its email address."
    )
    token = input("Reset token: ").strip()
    new_password = getpass.getpass("New password: ")
    confirmation = getpass.getpass("Confirm new password: ")
    if new_password != confirmation:
        console.print("[red]Passwords do not match.[/red]")
        return False
    try:
        client.confirm_password_reset(token, new_password)
        identity = client.login(email, new_password)
    except SpanglishAPIError as reset_error:
        console.print(f"[red]Password reset failed: {reset_error}[/red]")
        return False
    console.print(f"Password reset. [green]Authenticated[/green] as {identity}.")
    return True


def run() -> None:
    """Run the CLI and turn terminal interrupts into a clean exit."""
    try:
        main_menu()
    except QuitRequested, KeyboardInterrupt, EOFError:
        console.print("\n[bold red]Exiting Spanglish CLI. Goodbye![/bold red]\n")


if __name__ == "__main__":
    run()
