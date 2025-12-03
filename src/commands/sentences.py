import questionary
import typer
from rich.console import Console
from rich.table import Table

from src.db import crud
from src.enums import TopicEnum

app = typer.Typer(
    add_completion=False,
    help="📝 Sentence management commands: add, list sentences."
)
console = Console()

@app.command()
def add(interactive: bool = True):
    """Add a new sentence to the database."""
    while interactive:
        spanish = typer.prompt("Enter the Spanish sentence").strip()
        english = typer.prompt("Enter the English translation").strip()
        topic = questionary.select("Select a topic", choices=TopicEnum).ask()

        s = crud.create_sentence(spanish, english, topic)
        console.print(f"[green]Added:[/] {s.spanish} -> {s.english} ({s.topic})")

        more = typer.confirm("Add another sentence?", default=True)
        if not more:
            break


@app.command()
def list():
    """List all sentences in the database. Optionally filter by topic,
    limit the number of records, and randomize the selection.
    """
    topic = None
    with_topic = typer.confirm(
        "Do you want to filter by Topic ?", default=False
    )
    if with_topic:
        topic: TopicEnum = questionary.select(
            "Filter by topic (or select 'All' for no filter)",
            choices=TopicEnum,
        ).ask()

    limit: int = typer.prompt(
        "How many records ?",
        default=10,
        type=int
    )

    is_random: bool = typer.confirm(
        "Do you want the sentences in random order ?", default=False
    )

    sentences = crud.list_sentences(topic=topic, limit=limit, is_random=is_random)
    table = Table(title="Sentences")
    table.add_column("Spanish", style="cyan")
    table.add_column("English", style="green")
    table.add_column("Topic", style="magenta")

    for sentence in sentences:
        table.add_row(sentence.spanish, sentence.english, sentence.topic.value)

    console.print(table)
