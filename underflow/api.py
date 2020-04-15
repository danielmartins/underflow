from dataclasses import asdict
from http import HTTPStatus

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.logger import logger
from fastapi.responses import HTMLResponse
from pydantic.main import BaseModel

from underflow.settings import settings
from underflow.stackoverflow import StackOverflow, ThrottleException

app = FastAPI()

queries = {}

wrapper = StackOverflow(settings)

token = ""


class StackQuery(BaseModel):
    query: str
    page_direction: str = "forward"


def bg_get_next_pages(query: str, sort: str, order: str, many: int = 2):
    latest_page = max(queries[query].keys())
    logger.info(f"Latest page: {latest_page}")
    for i in range(latest_page + 1, latest_page + many + 1):
        logger.info(f"Getting page {i}")
        try:
            response = wrapper.search(query, page=i)
        except ThrottleException:
            logger.error("Limit reached")
            return
        if response:
            queries[query][i] = response
        else:
            logger.warning(f"No response for page {i}")


def build_response(data):
    return {
        "results": data,
        "has_more": wrapper.current_request["has_more"],
        "page_size": wrapper.current_request["page_size"],
        "total": wrapper.current_request["total"],
    }


@app.post("/search")
async def search(
    body: StackQuery,
    background_tasks: BackgroundTasks,
    page: int = 1,
    sort: str = "relevance",
    order: str = "desc",
):
    """
    Faz pesquisa no StackOverflow e armazena em memória o resultado
    Faz também pesquisa preemptivo sempre +2 páginas de consulta
    :param order: organização da pesquisa, desc or asc
    :param sort: ordenação da pesquisa, ex: relevance, score, activity e etc
    :param body: Corpo da requisição com o a query da pesquisa
    :param background_tasks: scheduler para execução da pesquisa preemptiva
    :param page: pagina desejada da consulta
    :return:
    """
    logger.info(f"Page: {page}")
    results = []
    if body.query not in queries:
        queries[body.query] = {}

    if body.query in queries:
        if page in queries[body.query]:
            if (page + 1) not in queries[body.query]:
                logger.info("Pre-loading more pages")
                background_tasks.add_task(
                    bg_get_next_pages, body.query, sort=sort, order=order
                )
            logger.info("Returning from pre-loaded")
            results = [asdict(q) for q in queries[body.query][page]]
        else:
            try:
                result = wrapper.search(body.query, page=page, sort=sort, order=order)
            except ThrottleException as e:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=e.data)

            queries[body.query] = {page: result}
            logger.info("Pre-loading more pages")
            background_tasks.add_task(bg_get_next_pages, body.query, sort, order)
            results = [asdict(q) for q in result]

    return build_response(results)


@app.get("/status")
async def status():
    """
    Retorna quantidade de pesquisas feitas e páginas carregadas em memória
    :return:
    """
    return {
        "token": wrapper.token,
        "results": {q: list(data.keys()) for q, data in queries.items()},
    }


@app.get("/token", response_class=HTMLResponse)
async def token(request: Request):
    """
    Faz redirect para obtenção do token
    """
    return """
    <script>
    var idx = window.location.hash.indexOf("#");
    var hash = idx != -1 ? window.location.hash.substring(idx+1) : "";
    window.location = "http://localhost:8000/token/grab?" + hash;
    </script>
    """


@app.get("/token/grab")
async def token(request: Request, access_token: str):
    """
    Recebe token do StackOverFlow
    """
    wrapper.token = access_token
    return {"token": access_token}
