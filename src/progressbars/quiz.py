from rich.progress import BarColumn, TaskProgressColumn, TextColumn

# define the progress bar tuple for quiz attempts
quiz_progress = (
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    TextColumn("({task.completed}/{task.total})"),
)
