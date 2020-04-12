import typer
from tabulate import tabulate

from underflow.stackoverflow import StackOverflow

app = typer.Typer()


def tab(items):
    return [
        [
            f"{item.title[:50]}...",
            item.answer_with_better_score().score,
            item.answer_with_better_score().link,
        ]
        for item in items
    ]


@app.command()
def ask(
    keywords: str,
    sort: str = typer.Option("relevance", help="Items sort.", show_default=True),
    order: str = typer.Option("desc", help="Elements order", show_default=True),
):
    typer.echo(f"Keywords: {keywords}")
    typer.echo("Searching...")
    sof = StackOverflow()
    extra_parameters = {"sort": sort, "order": order}
    items = tab(sof.search(keywords, **extra_parameters))
    typer.echo(tabulate(items, headers=["Question", "Votes", "Link"]))


if __name__ == "__main__":
    app()
