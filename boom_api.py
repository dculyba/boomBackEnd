"""Boom API implemented using Google Cloud Endpoints.

Defined here are the ProtoRPC messages needed to define Schemas for methods
as well as those methods defined in an API.
"""

__author__ = 'dculyba'

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

WEB_CLIENT_ID = '638374801515-v23gs1l7vvrarbeoa22ntilcq6240ho7.apps.googleusercontent.com'
LOCALHOST_WEB_CLIENT_ID = '638374801515-n10hc1195mq8jt42qu881uvdhbt9ogue.apps.googleusercontent.com'

package = 'Boom'


class Question(messages.Message):
  """Question that stores a message."""
  question = messages.StringField(1)


class QuestionCollection(messages.Message):
  """Collection of Questions."""
  questions = messages.MessageField(Question, 1, repeated=True)


STORED_QUESTIONS = QuestionCollection(questions=[
    Question(question='Is this chai?'),
    Question(question='Is this a lot?'),
])


@endpoints.api(name='boom', version='v1',
               allowed_client_ids=[WEB_CLIENT_ID,
                                   LOCALHOST_WEB_CLIENT_ID,
                                   endpoints.API_EXPLORER_CLIENT_ID],
               scopes=[endpoints.EMAIL_SCOPE] )
class BoomApi(remote.Service):
  """Boom API v1."""

  @endpoints.method(message_types.VoidMessage, QuestionCollection,
                    path='questions', http_method='GET',
                    name='questions.listQuestions')
  def questions_list(self, unused_request):
    return STORED_QUESTIONS

  MULTIPLY_METHOD_RESOURCE = endpoints.ResourceContainer(Question,
    times=messages.IntegerField(2, variant=messages.Variant.INT32,
                                required=True))

  @endpoints.method(MULTIPLY_METHOD_RESOURCE, Question,
                  path='questions/{times}', http_method='POST',
                  name='questions.multiply')
  def questions_multiply(self, request):
    return Question(question=request.question * request.times)

  ID_RESOURCE = endpoints.ResourceContainer(
      message_types.VoidMessage,
      id=messages.IntegerField(1, variant=messages.Variant.INT32))

  #@endpoints.method( <request class>, <response class>
  @endpoints.method(ID_RESOURCE, Question,
                    path='questions/{id}', http_method='GET',
                    name='questions.getQuestion')
  def question_get(self, request):
    try:
      return STORED_QUESTIONS.questions[request.id]
    except (IndexError, TypeError):
      raise endpoints.NotFoundException('Question %s not found.' %
                                        (request.id,))

APPLICATION = endpoints.api_server([BoomApi])