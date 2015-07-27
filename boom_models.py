#!/usr/bin/python


"""Helper model class for Boom API.

Defines models for persisting and querying score data on a per user basis and
provides a method for returning a 401 Unauthorized when no current user can be
determined.
"""

import logging

import endpoints
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import db

from boom_api_messages import QuestionResponseMessage
from boom_api_messages import QuestionAnswerMessage


TIME_FORMAT_STRING = '%b %d, %Y %I:%M:%S %p'

class User(db.Model):
    user = db.UserProperty(required=True)

def email_to_userid(address):
    """Return a stable user_id string based on an email address, or None if
    the address is not a valid/existing google account."""
    u = users.User(address)
    key = User(user=u).put()
    obj = User.get(key)
    return obj.user.user_id()

def get_endpoints_current_user(raise_unauthorized=True):
    """Returns a current user and (optionally) causes an HTTP 401 if no user.

    Args:
        raise_unauthorized: Boolean; defaults to True. If True, this method
            raises an exception which causes an HTTP 401 Unauthorized to be
            returned with the request.

    Returns:
        The signed in user if there is one, else None if there is no signed in
        user and raise_unauthorized is False.
    """
    current_user = endpoints.get_current_user()
    if raise_unauthorized and current_user is None:
        raise endpoints.UnauthorizedException('Invalid token.')
    return current_user

def get_key_for_user_id(userId):
    return ndb.Key("User", userId)

def safe_get_user_id_from_user(user):
    if user.user_id() != None:
        return user.user_id()
    elif user.email() != None:
        return email_to_userid(user.email())
    else:
        return "NO_USER_ID"

def get_key_for_user(user):
    return get_key_for_user_id( safe_get_user_id_from_user(user) )

class Question(ndb.Model):
    text = ndb.StringProperty(required=True, indexed=False)
    time_asked = ndb.DateTimeProperty(auto_now_add=True)
    asker_id = ndb.StringProperty(required=True)
    yes_count = ndb.IntegerProperty(indexed=False, default=0)
    no_count = ndb.IntegerProperty(indexed=False, default=0)

    @property
    def timestamp(self):
        """Property to format a datetime object to string."""
        return self.time_asked.strftime(TIME_FORMAT_STRING)

    def to_message(self):
        """Turns the Question entity into a ProtoRPC object.

        This is necessary so the entity can be returned in an API request.

        Returns:
            An instance of QuestionInsertResponseMessage with the ID set to the datastore
            ID of the current entity, the outcome simply the entity's outcome
            value and the played value equal to the string version of played
            from the property 'timestamp'.
        """
        return QuestionResponseMessage(id=self.key.id(),
                                text=self.text,
                                asker_id=self.asker_id,
                                asker_name=None,
                                time_asked = self.timestamp,
                                yes_count = self.yes_count,
                                no_count = self.no_count)

    @classmethod
    def put_from_message(cls, message):
        """Gets the current user and inserts a question.

        Args:
            message: A QuestionInsertMessage instance to be inserted.

        Returns:
            The Question entity that was inserted.
        """
        current_user_id = safe_get_user_id_from_user(get_endpoints_current_user())
        key = get_key_for_user_id(current_user_id)
        #entity = cls(parent=key,text=message.question_text, asker_id=current_user_id)
        entity = cls(text=message.question_text, asker_id=current_user_id)
        return_key = entity.put()
        return entity

    @classmethod
    def answer_from_message(cls, message):
        """Gets the current user and answers a question.

        Args:
            message: A QuestionAnswerMessage instance to be answered.

        Returns:
            The Question entity that was answered.
        """
        to_answer = cls.get_by_id(message.question_id)
        if to_answer != None:
            print "found answer 2!"
        if message.answer == QuestionAnswerMessage.Answer.YES:
            to_answer.yes_count += 1
        elif message.answer == QuestionAnswerMessage.Answer.NO:
            to_answer.no_count += 1
        to_answer.put()
        return to_answer

    @classmethod
    def query_current_user(cls):
        """Creates a query for the questions of the current user.

        Returns:
            An ndb.Query object bound to the current user. This can be used
            to filter for other properties or order by them.
        """
        current_user_id = safe_get_user_id_from_user(get_endpoints_current_user())
        return cls.query(cls.asker_id == current_user_id)

    @classmethod
    def query_user_id(cls, user_id):
        """Creates a query for the questions of the specified user.

        Returns:
            An ndb.Query object bound to the user id passed in. This can be used
            to filter for other properties or order by them.
        """
        return cls.query(cls.asker_id == user_id)

    @classmethod
    def query_all(cls):
        """Creates a query for all the questions.

        Returns:
            An ndb.Query object bound to the user id passed in. This can be used
            to filter for other properties or order by them.
        """
        return cls.query()

