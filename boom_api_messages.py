#!/usr/bin/python


"""ProtoRPC message class definitions for Boom API."""


from protorpc import messages

class QuestionResponseMessage(messages.Message):
    """ProtoRPC message definition to represent a question."""
    id = messages.IntegerField(1, required=True)
    text = messages.StringField(2, required=True)
    asker_id = messages.StringField(3, required=True)
    asker_name = messages.StringField(4, required=False)
    time_asked = messages.StringField(5)
    yes_count = messages.IntegerField(6)
    no_count = messages.IntegerField(7)

class QuestionInsertMessage(messages.Message):
    """ProtoRPC message definition to represent a question."""
    question_text = messages.StringField(1)

class QuestionAnswerMessage(messages.Message):
    """ProtoRPC message definition to represent an answer to a question."""
    question_id = messages.IntegerField(1, required=True)
    class Answer(messages.Enum):
        YES = 1
        NO = 2
        OTHER = 3
    answer = messages.EnumField(Answer, 2, required=True)
    answerer_id = messages.StringField(3)

class QuestionListRequest(messages.Message):
    """ProtoRPC message definition to represent the request of question list query."""
    limit = messages.IntegerField(1, default=10)
    class User(messages.Enum):
        ANY = 1
        CURRENT = 2
        SPECIFIC = 3
    user_type = messages.EnumField(User, 2, default=User.ANY)
    asker_id = messages.StringField(3, default=None)

class QuestionListResponse(messages.Message):
    """ProtoRPC message definition to represent the response to a question query."""
    questions = messages.MessageField(QuestionResponseMessage, 1, repeated=True)
