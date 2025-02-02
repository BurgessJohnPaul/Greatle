# -*- coding: utf-8 -*-

# This is Henry by Greatle

import logging
import boto3
import dynamo_helper
import journal_helper
import goal_helper
import discovery_helper
import speech_helper
import sentiment_helper
import random
import json
import string

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from meme_helper import get_meme

sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Greatle_Users')
GOAL_TO_DELETE_SESSION_ATTRIBUTE = "goal_to_delete"
LAST_QUERY_SESSION_ATTRIBUTE = "last_query"
LAST_QUERY_ID_SESSION_ATTRIBUTE = "last_query_id"
LAST_DOCUMENT_ID_SESSION_ATTRIBUTE = "last_document_id"
LAST_AUTHOR_SESSION_ATTRIBUTE = 'last_author'
card_title = 'Henry by Greatle'


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
            if 'user_name' in response['Item'] and response['Item']['user_name'] is not None:
                speech_text = "Hello, welcome back " + response['Item']['user_name'] + "! How may I assist you?"
            else:
                speech_text = "Hello, welcome back! How may I assist you?"
        else:
            speech_text = "Hello, welcome to Henry by Greatle. I am here to give you encouragement, advice, and help set and maintain goals. You can say 'Help' to learn more."
            dynamo_helper.put_item_to_users(user_id)
        card_text = speech_text

        handler_input.attributes_manager.session_attributes["drunk_mode_state"] = speech_helper.get_drunk_mode_state(user_id)

        return speech_helper.build_response(handler_input, card_title, card_text, speech_text, img_tuple=get_meme())


class UpdateNameIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("UpdateNameIntent")(handler_input)

    def handle(self, handler_input):
        user_id = handler_input.request_envelope.session.user.user_id[18:]
        slots = handler_input.request_envelope.request.intent.slots
        name = string.capwords(slots['Name'].value)
        dynamo_helper.update_name_from_users(user_id, name)
        speech_text = "Okay, I will call you " + name + " from now on"
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


class AdviceIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AdviceIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        print('session attributes:', handler_input.attributes_manager.session_attributes)
        print("Advice called")
        slots = handler_input.request_envelope.request.intent.slots
        print(slots)
        keywords = slots['AdviceTopic'].value
        print(keywords)
        handler_input.attributes_manager.session_attributes[LAST_QUERY_SESSION_ATTRIBUTE] = keywords
        queryResults = discovery_helper.query(keywords)
        print('query results:', queryResults)
        if queryResults is not None and isinstance(queryResults, (tuple, list)):
            passage = queryResults[0]
            docId = queryResults[1]
            queryId = queryResults[2]
            author = queryResults[3]

            speech_text = passage + "<break time='1s'/> Was that helpful?"
            card_text = passage + "\nWas that helpful?"
            handler_input.attributes_manager.session_attributes[LAST_QUERY_ID_SESSION_ATTRIBUTE] = queryId
            print('session attributes:', handler_input.attributes_manager.session_attributes)
            handler_input.attributes_manager.session_attributes[LAST_DOCUMENT_ID_SESSION_ATTRIBUTE] = docId
            handler_input.attributes_manager.session_attributes[LAST_AUTHOR_SESSION_ATTRIBUTE] = author
            print('session attributes:', handler_input.attributes_manager.session_attributes)
        elif queryResults is not None and isinstance(queryResults, str):
            speech_text = queryResults
            card_text = speech_text
            handler_input.attributes_manager.session_attributes[LAST_AUTHOR_SESSION_ATTRIBUTE] = None
        else:
            speech_text = 'I was unable to find anything on that subject.'
            card_text = speech_text

        clearSessionAttributes(handler_input, deleteQueryID=False)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


class CreateGoalIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("CreateGoalIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        user_id = handler_input.request_envelope.session.user.user_id[18:]
        slots = handler_input.request_envelope.request.intent.slots

        speech_text, is_remembered = goal_helper.create_goal_helper(user_id, slots)
        card_text = speech_text
        meme = get_meme('GetMotivated') if is_remembered else None
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text, img_tuple=meme)


class DeleteGoalIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("DeleteGoalIntent")(handler_input)

    def handle(self, handler_input):
        user_id = handler_input.request_envelope.session.user.user_id[18:]
        slots = handler_input.request_envelope.request.intent.slots

        speech_text, goal_description = goal_helper.retrieve_goal_to_delete_helper(user_id, slots)
        handler_input.attributes_manager.session_attributes[GOAL_TO_DELETE_SESSION_ATTRIBUTE] = goal_description
        card_text = speech_text
        clearSessionAttributes(handler_input, deleteGoalToDelete=False)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


class CompleteGoalIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("CompleteGoalIntent")(handler_input)

    def handle(self, handler_input):
        user_id = handler_input.request_envelope.session.user.user_id[18:]
        slots = handler_input.request_envelope.request.intent.slots

        speech_text = goal_helper.complete_goal_helper(user_id, slots)
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


class RetrieveGoalIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("RetrieveGoalIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        user_id = handler_input.request_envelope.session.user.user_id[18:]

        speech_text = goal_helper.retrieve_goal_helper(user_id)
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


class ListGoalIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("ListGoalIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        user_id = handler_input.request_envelope.session.user.user_id[18:]

        speech_text = goal_helper.list_goal_helper(user_id)
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


class ListCompletedGoalIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("ListCompletedGoalIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        user_id = handler_input.request_envelope.session.user.user_id[18:]

        speech_text = goal_helper.list_completed_goal_helper(user_id)
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


class JournalIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("JournalIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        user_id = handler_input.request_envelope.session.user.user_id[18:]
        slots = handler_input.request_envelope.request.intent.slots

        speech_text = journal_helper.create_journal_helper(user_id, slots)
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


class GetJournalIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("GetJournalIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        user_id = handler_input.request_envelope.session.user.user_id[18:]

        speech_text = journal_helper.get_random_journal_entry_helper(user_id)
        card_text = speech_text
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


class GetSentimentIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("GetSentimentIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        user_id = handler_input.request_envelope.session.user.user_id[18:]

        goal_list = dynamo_helper.list_goals(user_id)
        completed_goal_list = dynamo_helper.list_goals_with_status(user_id, "COMPLETED")
        journal_entries = journal_helper.get_all_entries(user_id)

        all_text = ""

        for goal in goal_list:
            all_text = all_text + goal + " "
        for goal in completed_goal_list:
            all_text = all_text + goal + " "
        for journal_entry in journal_entries:
            all_text = all_text + journal_entry["text"] + " "

        if all_text == "":
            speech_text = "You don't have any journal entries or goals. Add some so we know more about you."
        else:
            user_sentiment = sentiment_helper.sentiment_with_threshold(all_text)

            if user_sentiment == "HAPPY":
                speech_text = "You've been very happy. Keep it up! You're a positive force in the universe!"
            elif user_sentiment == "SLIGHTLY_HAPPY":
                speech_text = "You've been quite happy. That's pretty good."
            elif user_sentiment == "NEUTRAL":
                speech_text = "You've been feeling neutral. I have no feelings about this, one way or another."
            elif user_sentiment == "SLIGHTLY_SAD":
                speech_text = "It seems like you've been a little under the weather. That's okay. Tomorrow's a new day."
            elif user_sentiment == "SAD":
                speech_text = "It seems like you have not been feeling good. That's okay. Everybody feels sad " \
                              "sometimes."
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


class GetPersonalAdviceHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GetPersonalAdvice")(handler_input)

    def handle(self, handler_input):
        user_id = handler_input.request_envelope.session.user.user_id[18:]

        goal_list = dynamo_helper.list_goals(user_id)
        completed_goal_list = dynamo_helper.list_goals_with_status(user_id, "COMPLETED")
        journal_entries = journal_helper.get_all_entries(user_id)

        all_text = ""
        user_sentiment = ""

        for goal in goal_list:
            all_text = all_text + goal + " "
        for goal in completed_goal_list:
            all_text = all_text + goal + " "
        for journal_entry in journal_entries:
            all_text = all_text + journal_entry["text"] + " "

        if all_text == "":
            speech_text = "You don't have any journal entries or goals. Tell me more about yourself so I can give you relevant advice"
        else:
            user_sentiment = sentiment_helper.sentiment_with_threshold(all_text)

        if user_sentiment != "":
            query_word = sentiment_helper.get_query_word_from_sentiment(user_sentiment)
            handler_input.attributes_manager.session_attributes[LAST_QUERY_SESSION_ATTRIBUTE] = query_word
            queryResults = discovery_helper.query(query_word)
            print('query results:', queryResults)
            if queryResults is not None and isinstance(queryResults, (tuple, list)):
                passage = queryResults[0]
                docId = queryResults[1]
                queryId = queryResults[2]
                author = queryResults[3]

                speech_text = passage + "<break time='1s'/> Was that helpful?"
                card_text = passage + "\nWas that helpful?"
                handler_input.attributes_manager.session_attributes[LAST_QUERY_ID_SESSION_ATTRIBUTE] = queryId
                print('session attributes:', handler_input.attributes_manager.session_attributes)
                handler_input.attributes_manager.session_attributes[LAST_DOCUMENT_ID_SESSION_ATTRIBUTE] = docId
                handler_input.attributes_manager.session_attributes[LAST_AUTHOR_SESSION_ATTRIBUTE] = author
                print('session attributes:', handler_input.attributes_manager.session_attributes)
            elif queryResults is not None and isinstance(queryResults, str):
                speech_text = queryResults
                card_text = speech_text
                handler_input.attributes_manager.session_attributes[LAST_AUTHOR_SESSION_ATTRIBUTE] = None
            else:
                speech_text = 'Ask me later when you have used the skill more'
                card_text = speech_text

            clearSessionAttributes(handler_input, deleteQueryID=False)
        else:
            card_text = speech_text

        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "I can give you life advice. You can ask me for advice by saying something like 'I want advice" \
                      " about love'. Once I learn more about you, I can give you personal advice, just say give me personal advice" \
                      " I can also help you manage your goals. Say 'goal help' to learn more. I can keep " \
                      "a journal for you. Say 'journal help' to learn about this feature.  To learn about my other " \
                      "features, say 'more help'."
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


class GoalHelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("GoalHelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "I can help you keep track of your goals. You can add a new goal by saying something like 'I " \
                      "want to meet Hillary Clinton'. Then, if you achieve this, you can say 'I have" \
                      " completed my goal of meeting Hillary Clinton'. If you give up on your goal, you can say, " \
                      "'Delete my goal to meet Hillary Clinton'. You can ask me about your goals by saying 'List" \
                      " my goals' or 'List my completed goals.'"
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


class JournalHelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("JournalHelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "I can help you keep a journal. Say 'Open Journal' to add a new journal entry. You can say 'Read " \
                      "me my journal' to access your journal entries.'"
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


class OtherHelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("OtherHelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "If you want me to remember your name say something like call me Steven. If you liked a quote and" \
                      " want to know the author, just say who was the author. I can keep track of your mood, just ask " \
                      "how have I been. Also, you can say 'turn on drunk mode' to enable drunk mode."
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


class TurnOnDrunkModeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("TurnOnDrunkModeIntent")(handler_input)

    def handle(self, handler_input):
        user_id = handler_input.request_envelope.session.user.user_id[18:]
        speech_text = "Okay"
        card_text = speech_text
        speech_helper.set_drunk_mode(user_id, handler_input, True)
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text, img_tuple=get_meme('drunk'))


class TurnOffDrunkModeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("TurnOffDrunkModeIntent")(handler_input)

    def handle(self, handler_input):
        user_id = handler_input.request_envelope.session.user.user_id[18:]
        speech_text = "Fine"
        speech_helper.set_drunk_mode(user_id, handler_input, False)
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


class SuicidePreventionIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("SuicidePreventionIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = "I may not be the smartest bot out there, however, if you are having thoughts of suicide, " \
                      "please call the National Suicide Prevention Lifeline at 1-800-273-8255 (TALK) or go to " \
                      "SpeakingOfSuicide.com/resources for a list of additional resources."
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


class ThankYouIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("ThankYouIntent")(handler_input)

    def handle(self, handler_input):
        thanks = ["You're welcome!", "No problem amigo!", "Aww shucks, you are making me blush.", "No, thank YOU!"]
        speech_text = thanks[random.randint(0, len(thanks) - 1)] + " Here is a funny picture from Reddit, I hope."
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text, img_tuple=get_meme('funny'))


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
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text, end_session=True)

class LastAuthorIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("LastAuthorIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        if handler_input.request_envelope.session.attributes is not None and \
                handler_input.request_envelope.session.attributes.get(LAST_AUTHOR_SESSION_ATTRIBUTE) is not None:
            author = handler_input.attributes_manager.session_attributes[LAST_AUTHOR_SESSION_ATTRIBUTE]
            speech_text = "The author of the last quote was " + author
            image_tuple = (author, 'https://avatars.io/twitter/' + "".join(author.split()) + '/large', 'From Twitter')
        else:
            speech_text = "There are no recent quotes or the author is unavailable."
            image_tuple = None
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text, img_tuple=image_tuple)

def clearSessionAttributes(handler_input, deleteGoalToDelete=True, deleteQueryID=True):
    if handler_input.request_envelope.session.attributes is not None:
        if deleteGoalToDelete: handler_input.attributes_manager.session_attributes[GOAL_TO_DELETE_SESSION_ATTRIBUTE] = None
        if deleteQueryID: handler_input.attributes_manager.session_attributes[LAST_QUERY_ID_SESSION_ATTRIBUTE] = None


class YesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        user_id = handler_input.request_envelope.session.user.user_id[18:]
        if handler_input.request_envelope.session.attributes is not None and \
                handler_input.request_envelope.session.attributes.get(GOAL_TO_DELETE_SESSION_ATTRIBUTE) is not None:
            dynamo_helper.delete_goal(user_id, handler_input.request_envelope.session.attributes[
                GOAL_TO_DELETE_SESSION_ATTRIBUTE])
            speech_text = "Okay, I deleted that goal"
        elif handler_input.request_envelope.session.attributes is not None and handler_input.request_envelope.session.attributes.get(LAST_QUERY_ID_SESSION_ATTRIBUTE) is not None:
            speech_text = "Good. I'll record that."
            discovery_helper.rateQuery(handler_input.request_envelope.session.attributes[
                LAST_QUERY_ID_SESSION_ATTRIBUTE], handler_input.request_envelope.session.attributes[
                LAST_DOCUMENT_ID_SESSION_ATTRIBUTE], relevant=True)
        else:
            speech_text = "Sorry, I am unsure why you said yes. Please start your intent over."
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


class NoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        if handler_input.request_envelope.session.attributes is not None and handler_input.request_envelope.session.attributes.get(GOAL_TO_DELETE_SESSION_ATTRIBUTE) is not None:
            speech_text = "Okay, I will not delete that goal"
        elif handler_input.request_envelope.session.attributes is not None and handler_input.request_envelope.session.attributes.get(LAST_QUERY_ID_SESSION_ATTRIBUTE) is not None:
            speech_text = "Sorry, I'll take note of that."
            discovery_helper.rateQuery(handler_input.request_envelope.session.attributes[
                                           LAST_QUERY_ID_SESSION_ATTRIBUTE],
                                       handler_input.request_envelope.session.attributes[
                                           LAST_DOCUMENT_ID_SESSION_ATTRIBUTE], relevant=False)
        else:
            speech_text = "Sorry, I am unsure why you said no. Please start your intent over."
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


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
        card_text = speech_text
        clearSessionAttributes(handler_input)
        return speech_helper.build_response(handler_input, card_title, card_text, speech_text)


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

sb.add_request_handler(JournalIntentHandler())
sb.add_request_handler(GetJournalIntentHandler())

sb.add_request_handler(GetSentimentIntentHandler())

sb.add_request_handler(TurnOnDrunkModeHandler())
sb.add_request_handler(TurnOffDrunkModeHandler())
sb.add_request_handler(SuicidePreventionIntentHandler())

sb.add_request_handler(GoalHelpIntentHandler())
sb.add_request_handler(JournalHelpIntentHandler())
sb.add_request_handler(OtherHelpIntentHandler())

sb.add_request_handler(ThankYouIntentHandler())
sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(UpdateNameIntentHandler())
sb.add_request_handler(LastAuthorIntentHandler())
sb.add_request_handler(GetPersonalAdviceHandler())

sb.add_exception_handler(CatchAllExceptionHandler())


handler = sb.lambda_handler()