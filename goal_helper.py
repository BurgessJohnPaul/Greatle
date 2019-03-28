import random
import dynamo_helper
import language_helper
from time import strftime
import similarity_helper


DATE_FORMAT = "%Y-%m-%d"
NO_DATE = "NO_DATE"
congrats = ["Congrats!", "Great work!", "Keep on rockin' it!", "Go Bucks!", "Keep it up!"]


def create_goal_helper(user_id, slots):
    if slots is None or "Goal" not in slots or "GoalPhrase" not in slots:
        speech_text = "I have no idea what is going on with these slots today please send help"
    else:
        goal = slots['Goal'].value
        goal_phrase = slots['GoalPhrase'].value

        if goal is None and goal_phrase is None:
            speech_text = "I don't understand your goal. Could you rephrase it?"
        else:
            speech_text = "Sure I'll remember that!"

            if goal is None:
                goal_value = goal_phrase
            else:
                goal_value = goal

            if slots["DATE"].value is not None:
                dynamo_helper.create_goal(user_id, goal_value, strftime(DATE_FORMAT), slots["DATE"].value)
            else:
                dynamo_helper.create_goal(user_id, goal_value, strftime(DATE_FORMAT), NO_DATE)

    return speech_text


def retrieve_goal_helper(user_id):
    response = dynamo_helper.get_item_from_users(user_id)

    if 'Item' in response:
        if 'goal' in response['Item']:
            speech_text = "Your goal was to " + response['Item']['goal']
        else:
            speech_text = "It doesn't seem like you have set any goals recently,"
    else:
        speech_text = "There was a terrible error"

    return speech_text


def list_goal_helper(user_id):
    goal_list = dynamo_helper.list_goals(user_id)

    if len(goal_list) == 0:
        speech_text = "You do not have any active goals. Create a new goal by saying something like: 'I want to go to the gym today'"
    else:
        if len(goal_list) == 1:
            speech_text = "Your goal is to " + goal_list[0]
        else:
            speech_text = "Your goals are to "
            for ind, goal in enumerate(goal_list):
                if ind == len(goal_list) - 1:
                    speech_text += "and " + goal
                else:
                    speech_text += goal + ", "

    return speech_text


def list_completed_goal_helper(user_id):
    goal_list = dynamo_helper.list_goals_with_status(user_id, "COMPLETED")

    if len(goal_list) == 0:
        speech_text = "You have not completed any goals. Get off the couch and do something for once.'"
    else:
        if len(goal_list) == 1:
            speech_text = "Your completed goal was to " + goal_list[0]
        else:
            speech_text = "Your completed goals were to "
            for ind, goal in enumerate(goal_list):
                if ind == len(goal_list) - 1:
                    speech_text += "and " + goal
                else:
                    speech_text += goal + ", "

    return speech_text


def complete_goal_helper(user_id, slots):
    # the goal slot in the intent should be required
    if slots is None:
        # should not happen, but check here in case this intent somehow gets called
        speech_text = "Sorry, I did not understand what you said there. Can you say it again or word it differently?"
    else:
        goal_list = dynamo_helper.list_goals(user_id)
        if len(goal_list) == 0:
            speech_text = "Sorry you do not have any active goals to complete"
        else:
            # If you can connect to tensor flow model use that, otherwise use language_helper
            similarity_list = similarity_helper.match_similarity_with_list(slots['Goal'].value, goal_list)
            if similarity_list is not None and similarity_list[0][0] is not None and similarity_list[0][1] is not None:
                print("Using similarity server")
                most_similar_string = similarity_list[0][0]
                similar_value = similarity_list[0][1]
            else:
                most_similar_string, similar_value = language_helper.get_most_similar_string(slots['Goal'].value, goal_list)
                print("Most similar string: ", most_similar_string)
                print("Similarity value: ", similar_value)

            # Check here right now just in case we dont want to return something if they say something that is not like
            # one of their goals
            if similar_value >= 0.6:
                goal_description = most_similar_string
                dynamo_helper.update_goal_status(user_id, goal_description, "COMPLETED")
                speech_text = "I have marked your goal to " + goal_description + " as completed. " + congrats[random.randint(0, len(congrats) - 1)]
            else:
                # Maybe if we get here, we could ask if we should list the goals (add info to session_attributes)
                speech_text = "Sorry, you do not have a goal to " + slots['Goal'].value + ". You can ask me to list your goals if you want."

    return speech_text


def retrieve_goal_to_delete_helper(user_id, slots):
    # the goal slot in the intent should be required
    if slots is None:
        # should not happen, but check here in case this intent somehow gets called
        speech_text = "Sorry, I did not understand what you said there. Can you say it again or word it differently?"
        goal_description = None
    else:
        goal_list = dynamo_helper.list_goals(user_id)
        if len(goal_list) == 0:
            speech_text = "Sorry you do not have any active goals to delete"
            goal_description = None
        else:
            # If you can connect to tensor flow model use that, otherwise use language_helper
            similarity_list = similarity_helper.match_similarity_with_list(slots['Goal'].value, goal_list)
            if similarity_list is not None and similarity_list[0][0] is not None and similarity_list[0][1] is not None:
                print("Using similarity server")
                most_similar_string = similarity_list[0][0]
                similar_value = similarity_list[0][1]
            else:
                most_similar_string, similar_value = language_helper.get_most_similar_string(slots['Goal'].value, goal_list)
                print("Most similar string: ", most_similar_string)
                print("Similarity value: ", similar_value)

            # Check here right now just in case we dont want to return something if they say something that is not like
            # one of their goals
            if similar_value >= .7:
                speech_text = "Are you sure you want me to delete your goal to " + most_similar_string + "?"
                goal_description = most_similar_string
            else:
                # Maybe if we get here, we could ask if we should list the goals (add info to session_attributes)
                speech_text = "Sorry, you do not have a goal to " + slots['Goal'].value + ". You can ask me to list your goals if you want."
                goal_description = None

    return speech_text, goal_description

