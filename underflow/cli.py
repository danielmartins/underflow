import json
import webbrowser
from http import HTTPStatus

import httpx
import typer
import uvicorn
from dacite import from_dict
from tabulate import tabulate

from underflow import telegram
from underflow.settings import settings
from underflow.stackoverflow import STACK_OATH_URL, Question

app = typer.Typer()


def style_question(message, reduce=True):
    if reduce:
        message = f"{message[:50]}..."
    return typer.style(message, fg=typer.colors.YELLOW, bold=True)


def style_votes(message):
    return typer.style(message, fg=typer.colors.BRIGHT_MAGENTA, bold=True)


def style_link(message):
    return typer.style(message, fg=typer.colors.BRIGHT_BLUE, bold=True)


def tab(items):
    reconstructed_items = [from_dict(Question, item) for item in items["results"]]
    return [
        [
            style_question(item.title),
            style_votes(str(item.answer_with_better_score().score)),
            style_link(item.answer_with_better_score().link),
        ]
        for item in reconstructed_items
    ]


@app.command()
def ask(
    query: str,
    page: int = typer.Option(1, help="Which page to show", show_default=True),
    sort: str = typer.Option("relevance", help="Items sort.", show_default=True),
    order: str = typer.Option("desc", help="Elements order", show_default=True),
):
    query_fmt = typer.style(f"{query}", fg=typer.colors.YELLOW, bold=True)
    typer.echo("Searching for..." + query_fmt)
    result = httpx.post(
        "http://localhost:8000/search",
        params={"sort": sort, "order": order, "page": page},
        json={"query": query},
    )
    if result.status_code != HTTPStatus.OK:
        typer.secho("Cant do the search")
        typer.secho(
            json.dumps(result.json(), sort_keys=True, indent=4, separators=(",", ": ")),
            fg=typer.colors.RED,
        )
        return

    all_result = result.json()
    items = tab(all_result)
    if items:

        typer.echo(
            tabulate(
                items,
                headers=[
                    style_question("Question"),
                    style_votes("Votes"),
                    style_link("Link"),
                ],
            )
        )
        typer.echo("-" * 100)
        typer.secho(f"Total found: {all_result['total']}", fg=typer.colors.BRIGHT_GREEN)
        typer.secho(
            f"Page size: {all_result['page_size']}", fg=typer.colors.BRIGHT_CYAN
        )
        pages = round(all_result["total"] / all_result["page_size"])
        typer.secho(
            f"Available pages: {pages}", fg=typer.colors.BRIGHT_CYAN,
        )
        typer.echo("-" * 100)
    else:
        typer.secho(
            "No results find or cant execute the search", fg=typer.colors.MAGENTA
        )


@app.command()
def bot_server():
    typer.echo(f"Telegram bot server...")
    telegram.main()


@app.command()
def authenticate():
    webbrowser.get(using="google-chrome").open(STACK_OATH_URL)


@app.command()
def start_api():
    uvicorn.run("underflow.api:app", host="127.0.0.1", port=8000, log_level="debug")


@app.command()
def config():
    print(settings.dict())


if __name__ == "__main__":
    app()
