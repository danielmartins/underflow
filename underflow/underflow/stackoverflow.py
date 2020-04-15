from dataclasses import dataclass
from http import HTTPStatus
from typing import List

import httpx

from underflow.settings import settings as default_settings

STACK_OATH_URL = (
    f"https://stackoverflow.com/oauth/dialog?"
    f"client_id={default_settings.sck_client_id}&scope=no_expiry&redirect_uri={default_settings.sck_redirect_uri}"
)


@dataclass
class Answer:
    score: int
    link: str

    @staticmethod
    def make(data):
        permalink = f"https://stackoverflow.com/a/{data['answer_id']}"
        return Answer(score=data["score"], link=permalink)


@dataclass
class Question:
    title: str
    answers: List[Answer]

    def answer_with_better_score(self):
        if not self.answers:
            return Answer(score=0, link="No response yet")
        return max(self.answers, key=lambda k: k.score)


class StackOverflow:
    BASE_URL = "https://api.stackexchange.com"
    VERSION = "2.2"

    def __init__(self, settings=None):
        self._token = ""
        self.settings = settings or default_settings

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        self._token = token

    @staticmethod
    def url():
        return f"{StackOverflow.BASE_URL}/{StackOverflow.VERSION}"

    def default_query_params(self):
        base = {"site": "stackoverflow", "filter": "!9Z(-x.0nI"}
        if self._token:
            base.update(
                {"access_token": self._token, "key": self.settings.sck_client_key}
            )
        return base

    @staticmethod
    def extract_question_ids(data):
        result = []
        if data["items"]:
            result = [q["question_id"] for q in data["items"]]
        return result

    @staticmethod
    def _extract_titles(data):
        return {q["question_id"]: q["title"] for q in data["items"]}

    def extract_wrapper(self, response):
        self.current_request = response

    def search(
        self,
        questions: str,
        sort: str = "relevance",
        order: str = "desc",
        page: int = 1,
        **kwargs,
    ) -> List[Question]:
        query_params = {
            **self.default_query_params(),
            "intitle": questions,
            "page": page,
            "sort": sort,
            "order": order,
            **kwargs,
        }
        with httpx.Client(base_url=self.url()) as client:
            response = client.get(f"/{self.VERSION}/search", params=query_params)
            if response.status_code != HTTPStatus.OK:
                return self.handle_error(response)

            result = response.json()
            self.extract_wrapper(result)
            titles = self._extract_titles(result)
            question_ids = self.extract_question_ids(result)
            if not question_ids:
                return []

            answers = self._answers_for(client, question_ids)
            return [
                Question(title=titles.get(item), answers=answers.get(item),)
                for item in question_ids
            ]

    def _answers_for(self, client, question_ids: list) -> dict:
        str_ids = list(map(str, question_ids))
        response = client.get(
            f"{self.VERSION}/questions/{';'.join(str_ids)}/answers",
            params=self.default_query_params(),
        )
        answers = {question_id: [] for question_id in question_ids}
        for item in response.json()["items"]:
            answers[item["question_id"]].append(Answer.make(item))
        return answers

    def handle_error(self, response):
        if response.status_code == HTTPStatus.BAD_REQUEST:
            self._last_exception = ThrottleException(
                "Free limit reached", data=response.json()
            )
            raise self._last_exception


class ThrottleException(Exception):
    def __init__(self, *args: object, data: dict) -> None:
        super().__init__(*args)
        self._error_data = data

    @property
    def data(self):
        return self._error_data
