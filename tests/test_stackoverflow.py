import respx
from assertpy import assert_that

from underflow.stackoverflow import Question, StackOverflow


def test_search_questions(mocked_api):
    with respx.mock:
        stack = StackOverflow()
        response = stack.search("flask")

        assert_that(mocked_api["questions"].called).is_true()
        assert_that(mocked_api["answers"].called).is_true()
        assert_that(response).is_instance_of(list)
        assert_that(response[0]).is_instance_of(Question)
