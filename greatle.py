# -*- coding: utf-8 -*-

# This is Henry by Greatle

import logging
import boto3
import dynamo_helper
import goal_helper
import discovery_helper
import random
import json

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response


from language_helper import get_passages

sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Greatle_Users')
GOAL_TO_DELETE_SESSION_ATTRIBUTE = "goal_to_delete"
LAST_QUERY_SESSION_ATTRIBUTE = "last_query"
LAST_QUERY_ID_SESSION_ATTRIBUTE = "last_query_id"
LAST_DOCUMENT_ID_SESSION_ATTRIBUTE = "last_document_id"
card_title = 'Henry by Greatle'

def addSessionAttribute(handler_input, attribute, value):
    if handler_input.request_envelope.session.attributes is None:
        handler_input.attributes_manager.session_attributes = \
            {attribute: value}
    else:
        handler_input.attributes_manager.session_attributes[attribute] = value

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        #print("HandlerInput: ", handler_input.attributes_manager.session_attributes)
        print("HandlerInput with requestenvelope: ", handler_input.request_envelope.session.user.user_id)

        user_id = handler_input.request_envelope.session.user.user_id[18:]
        response = dynamo_helper.get_item_from_users(user_id)

        if 'Item' in response:
            if 'user_name' in response['Item']:
                speech_text = "Hello, welcome back " + response['Item']['user_name'] + "! How may I assist you?"
            else:
                speech_text = "Hello, welcome back! How may I assist you?"
        else:
            speech_text = "Hello, welcome to Greatle. I am here to give you encouragement, advice, and help set and maintain goals. How may I assist you?"
            dynamo_helper.put_item_to_users(user_id)

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(card_title, speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class UpdateNameIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("UpdateNameIntent")(handler_input)

    def handle(self, handler_input):
        user_id = handler_input.request_envelope.session.user.user_id[18:]
        slots = handler_input.request_envelope.request.intent.slots
        name = slots['Name'].value
        dynamo_helper.update_name_from_users(user_id, name)
        speech_text = "Okay, I will call you " + name + " from now on"
        handler_input.response_builder.speak(speech_text).set_card(SimpleCard(card_title, speech_text)).set_should_end_session(False)
        return handler_input.response_builder.response


class AdviceIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AdviceIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        #speech_text = "You are more capable than you imagine!"
        print("Advice called")
        slots = handler_input.request_envelope.request.intent.slots
        print(slots)
        keywords = slots['AdviceTopic'].value
        print(keywords)
        addSessionAttribute(handler_input, LAST_QUERY_SESSION_ATTRIBUTE, keywords)
        query, queryId = discovery_helper.query(keywords)
        if query.get_result()['matching_results'] > 0:
            speech_text = query.get_result()["passages"][0]['passage_text']
            docId = query.get_result()["passages"][0]['document_id']
            speech_text = "<speak>" + speech_text + "<break time='2s'/> Was that helpful?" + "</speak>"
            addSessionAttribute(handler_input, LAST_QUERY_ID_SESSION_ATTRIBUTE, queryId)
            print('session attributes:', handler_input.attributes_manager.session_attributes)
            addSessionAttribute(handler_input, LAST_DOCUMENT_ID_SESSION_ATTRIBUTE, docId)
            print(handler_input.attributes_manager.session_attributes)
        else:
            speech_text = 'I was unable to find anything on that subject.'
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(card_title, speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class CreateGoalIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("CreateGoalIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        user_id = handler_input.request_envelope.session.user.user_id[18:]
        slots = handler_input.request_envelope.request.intent.slots

        speech_text = goal_helper.create_goal_helper(user_id, slots)

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(card_title, speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class DeleteGoalIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("DeleteGoalIntent")(handler_input)

    def handle(self, handler_input):
        user_id = handler_input.request_envelope.session.user.user_id[18:]
        slots = handler_input.request_envelope.request.intent.slots

        speech_text, goal_description = goal_helper.retrieve_goal_to_delete_helper(user_id, slots)
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(card_title, speech_text)).set_should_end_session(
            False)

        addSessionAttribute(handler_input, GOAL_TO_DELETE_SESSION_ATTRIBUTE, goal_description)
        return handler_input.response_builder.response


class CompleteGoalIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("CompleteGoalIntent")(handler_input)

    def handle(self, handler_input):
        user_id = handler_input.request_envelope.session.user.user_id[18:]
        slots = handler_input.request_envelope.request.intent.slots

        speech_text = goal_helper.complete_goal_helper(user_id, slots)

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(card_title, speech_text)).set_should_end_session(
            False)

        return handler_input.response_builder.response


class RetrieveGoalIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("RetrieveGoalIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        user_id = handler_input.request_envelope.session.user.user_id[18:]

        speech_text = goal_helper.retrieve_goal_helper(user_id)

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(card_title, speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class ListGoalIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("ListGoalIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        user_id = handler_input.request_envelope.session.user.user_id[18:]

        speech_text = goal_helper.list_goal_helper(user_id)

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(card_title, speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class ListCompletedGoalIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("ListCompletedGoalIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        user_id = handler_input.request_envelope.session.user.user_id[18:]

        speech_text = goal_helper.list_completed_goal_helper(user_id)

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(card_title, speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "I can give you life advice. You can ask me for advice by saying something like 'I want advice" \
                      " about love'. I can also help you manage your goals. Say 'goal help' to learn more. If you want"\
                      " to learn about my other features, like drunk mode, say 'other help'."

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(card_title, speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class GoalHelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("GoalHelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "I can help you keep track of your goals. You can add a new goal by saying something like 'I " \
                      "want to meet Hillary Clinton'. Then, if you achieve this, you can say 'I have" \
                      " completed my goal of meeting Hillary Clinton'. If you give up on your goal, you can can say, " \
                      "'Delete my goal to meet Hillary Clinton'. You can ask me about your goals by saying 'List" \
                      " my goals' or 'List my completed goals.'"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(card_title, speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class OtherHelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("OtherHelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "You can say 'turn on drunk mode' to make me talk differently. If you want me to tell you a " \
                      "story, you can say 'tell me a koan.'"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(card_title, speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        user_id = handler_input.request_envelope.session.user.user_id[18:]
        response = dynamo_helper.get_item_from_users(user_id)

        with open("greetings.json") as f:
            data = json.load(f)

        goodbyes = data["goodbyes"]

        if 'Item' in response and 'user_name' in response['Item']:
            name = response['Item']['user_name']
            response_options = [x.replace("$name", name) for x in goodbyes]
        else:
            response_options = [x.replace("$name", "") for x in goodbyes]

        speech_text = random.choice(response_options)

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(card_title, speech_text))
        return handler_input.response_builder.response


class YesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        user_id = handler_input.request_envelope.session.user.user_id[18:]
        if handler_input.request_envelope.session.attributes is not None and \
                handler_input.request_envelope.session.attributes.get(GOAL_TO_DELETE_SESSION_ATTRIBUTE) is not None:
            dynamo_helper.delete_goal(user_id, handler_input.request_envelope.session.attributes[
                GOAL_TO_DELETE_SESSION_ATTRIBUTE])
            handler_input.attributes_manager.session_attributes[GOAL_TO_DELETE_SESSION_ATTRIBUTE] = None
            speech_text = "Okay, I deleted that goal"
        elif handler_input.request_envelope.session.attributes is not None and LAST_QUERY_ID_SESSION_ATTRIBUTE in handler_input.request_envelope.session.attributes:
            #speech_text = "The last query was " + handler_input.request_envelope.session.attributes[
            #    LAST_QUERY_SESSION_ATTRIBUTE]
            speech_text = "Good. I'll record that."
            discovery_helper.rateQuery(handler_input.request_envelope.session.attributes[
                LAST_QUERY_ID_SESSION_ATTRIBUTE], handler_input.request_envelope.session.attributes[
                LAST_DOCUMENT_ID_SESSION_ATTRIBUTE], relevant=True)
            handler_input.attributes_manager.session_attributes[LAST_QUERY_ID_SESSION_ATTRIBUTE] = None
        else:
            speech_text = "Sorry, I am unsure why you said yes. Please start your intent over."

        handler_input.response_builder.speak(speech_text).set_should_end_session(False)
        return handler_input.response_builder.response


class NoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        if handler_input.request_envelope.session.attributes is not None and GOAL_TO_DELETE_SESSION_ATTRIBUTE in handler_input.request_envelope.session.attributes:
            speech_text = "Okay, I will not delete that goal"
        elif handler_input.request_envelope.session.attributes is not None and LAST_QUERY_ID_SESSION_ATTRIBUTE in handler_input.request_envelope.session.attributes:
            speech_text = "Sorry, I'll take note of that."
            discovery_helper.rateQuery(handler_input.request_envelope.session.attributes[
                                           LAST_QUERY_ID_SESSION_ATTRIBUTE],
                                       handler_input.request_envelope.session.attributes[
                                           LAST_DOCUMENT_ID_SESSION_ATTRIBUTE], relevant=False)
            handler_input.attributes_manager.session_attributes[LAST_QUERY_ID_SESSION_ATTRIBUTE] = None
        else:
            speech_text = "Sorry, I am unsure why you said no. Please start your intent over."

        handler_input.response_builder.speak(speech_text).set_should_end_session(False)
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "I don't understand your command. Say 'help' for a list of commands."
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(card_title, speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)
        print(exception)
        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AdviceIntentHandler())
sb.add_request_handler(CreateGoalIntentHandler())
sb.add_request_handler(CompleteGoalIntentHandler())
sb.add_request_handler(RetrieveGoalIntentHandler())
sb.add_request_handler(ListGoalIntentHandler())
sb.add_request_handler(DeleteGoalIntentHandler())
sb.add_request_handler(ListCompletedGoalIntentHandler())
sb.add_request_handler(GoalHelpIntentHandler())
sb.add_request_handler(OtherHelpIntentHandler())

sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(UpdateNameIntentHandler())

sb.add_exception_handler(CatchAllExceptionHandler())


handler = sb.lambda_handler()