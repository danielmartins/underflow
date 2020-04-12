from dataclasses import dataclass
from typing import List
from urllib.parse import quote

import httpx


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
    ALLOWED_PARAMS = [
        "page",
        "todate",
        "pagesize",
        "fromdate",
        "todate",
        "order",
        "min",
        "max",
        "sort",
        "tagged",
        "nottagged",
        "intitle",
    ]

    @staticmethod
    def url():
        return f"{StackOverflow.BASE_URL}/{StackOverflow.VERSION}"

    def default_query_params(self):
        return {"site": "stackoverflow"}

    @staticmethod
    def extract_question_ids(data):
        return [q["question_id"] for q in data["items"]]

    @staticmethod
    def _extract_titles(data):
        return {q["question_id"]: q["title"] for q in data["items"]}

    def search(self, questions: str, **kwargs) -> List[Question]:
        with httpx.Client(base_url=self.url()) as client:
            query_params = {
                **self.default_query_params(),
                "intitle": questions,
                **kwargs,
            }
            response = client.get("/search", params=query_params).json()
            titles = self._extract_titles(response)
            question_ids = self.extract_question_ids(response)
            answers = self._answers_for(client, question_ids)
            return [
                Question(title=titles.get(item), answers=answers.get(item),)
                for item in question_ids
            ]

    def _answers_for(self, client, question_ids: list) -> dict:
        str_ids = list(map(str, question_ids))
        response = client.get(
            f"/questions/{';'.join(str_ids)}/answers",
            params=self.default_query_params(),
        )
        answers = {question_id: [] for question_id in question_ids}
        for item in response.json()["items"]:
            answers[item["question_id"]].append(Answer.make(item))
        return answers
