import dynamo_helper
import language_helper
from time import strftime

DATE_FORMAT = "%Y-%m-%d"

def create_goal_helper(user_id, slots):

    if slots is None or "Goal" not in slots:
        speech_text = "I have no idea what is going on with these slots today please send help"
    else:
        goal = slots['Goal'].value
        if slots["DATE"].value is not None:
            dynamo_helper.create_goal(user_id, goal, strftime(DATE_FORMAT), slots["DATE"].value)
        else:
            dynamo_helper.create_goal(user_id, goal, strftime(DATE_FORMAT), "")

        speech_text = "Sure I'll remember that!"

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
        speech_text = "Your goals are to "
        for goal in goal_list:
            speech_text += " " + goal

    return speech_text


def retrieve_goal_to_delete_helper(user_id, slots):
    # the goal slot in the intent should be required
    if slots is None:
        # should not happen, but check here in case this intent somehow gets called
        speech_text = "Sorry, I did not understand what you said there. Can you say it again or word it differently?"
    else:
        goal_list = dynamo_helper.list_goals(user_id)
        if len(goal_list) == 0:
            speech_text = "Sorry you do not have any active goals to delete"
        else:
            most_similar_string, similar_value = language_helper.get_most_similar_string(slots['Goal'].value, goal_list)
            print("Most similar string: ", most_similar_string)
            print("Similarity value: ", similar_value)
            # Check here right now just in case we dont want to return something if they say something that is not like
            # one of their goals
            if similar_value >= .7:
                speech_text = "Are you sure you want me to delete your goal to " + most_similar_string + "?"
            else:
                # Maybe if we get here, we could ask if we should list the goals (add info to session_attributes)
                speech_text = "Sorry, you do not have a goal to " + slots['Goal'].value

    return speech_text

