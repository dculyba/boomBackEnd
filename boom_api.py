"""Boom API implemented using Google Cloud Endpoints.

Defined here are the ProtoRPC messages needed to define Schemas for methods
as well as those methods defined in an API.
"""

__author__ = 'dculyba'


import endpoints
from protorpc import remote

from boom_models import Question
from boom_api_messages import QuestionListRequest
from boom_api_messages import QuestionListResponse
from boom_api_messages import QuestionInsertMessage
from boom_api_messages import QuestionResponseMessage
from boom_api_messages import QuestionAnswerMessage

WEB_CLIENT_ID = '638374801515-v23gs1l7vvrarbeoa22ntilcq6240ho7.apps.googleusercontent.com'
LOCALHOST_WEB_CLIENT_ID = '638374801515-n10hc1195mq8jt42qu881uvdhbt9ogue.apps.googleusercontent.com'

package = 'Boom'

@endpoints.api(name='boom', version='v1',
               allowed_client_ids=[WEB_CLIENT_ID,
                                   LOCALHOST_WEB_CLIENT_ID,
                                   endpoints.API_EXPLORER_CLIENT_ID],
               scopes=[endpoints.EMAIL_SCOPE] )
class BoomApi(remote.Service):
    """Boom API v1."""
    @endpoints.method(QuestionListRequest, QuestionListResponse,
                      path='questions', http_method='GET',
                      name='questions.listQuestions')
    def questions_list(self, request):
        """Exposes an API endpoint to query for questions for the current user.

        Args:
            request: An instance of QuestionListRequest parsed from the API
                request.

        Returns:
            An instance of QuestionListResponse containing the questions for the
            current user returned in the query. If the API request specifies an
            order of WHEN (the default), the results are ordered by time from
            most recent to least recent. If the API request specifies an order
            of TEXT, the results are ordered by the string value of the scores.
        """
        if request.user_type == QuestionListRequest.User.ANY:
            query = Question.query_all()
        elif request.user_type == QuestionListRequest.User.CURRENT:
            query = Question.query_current_user()
        elif request.user_type == QuestionListRequest.User.SPECIFIC:
            query = Question.query_user_id(request.asker_id)
        #Default sorting is by asked date
        query = query.order(-Question.time_asked)
        items = [entity.to_message() for entity in query.fetch(request.limit)]
        return QuestionListResponse(questions=items)

    @endpoints.method(QuestionInsertMessage, QuestionResponseMessage,
                      path='questionsInsert', http_method='POST',
                      name='questions.insertQuestion')
    def question_insert(self, request):
        """Exposes an API endpoint to insert a score for the current user.

        Args:
            request: An instance of QuestionInsertMessage parsed from the API
                request.

        Returns:
            An instance of QuestionResponseMessage containing all the details of the question inserted,
            time, id, askerId, etc.
        """
        entity = Question.put_from_message(request)
        if entity != None:
            return entity.to_message()
        return None

    @endpoints.method(QuestionAnswerMessage, QuestionResponseMessage,
                      path='questionsAnswer', http_method='POST',
                      name='questions.answerQuestion')
    def question_answer(self, request):
        """Exposes an API endpoint to insert a score for the current user.

        Args:
            request: An instance of QuestionInsertMessage parsed from the API
                request.

        Returns:
            An instance of QuestionResponseMessage containing all the details of the question inserted,
            time, id, askerId, etc.
        """
        entity = Question.answer_from_message(request)
        if entity != None:
            return entity.to_message()
        return None

APPLICATION = endpoints.api_server([BoomApi])