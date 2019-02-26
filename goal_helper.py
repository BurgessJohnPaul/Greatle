import dynamo_helper


def create_goal_helper(user_id, slots):

    if slots == None or "Goal" not in slots:
        speech_text = "I have no idea what is going on with these slots today please send help"
    else:
        goal = slots['Goal'].value
        dynamo_helper.create_goal(user_id, goal, "PLACEHOLDERDATE1", "PLACEHOLDERDATE2")

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
            speech_text.append(goal)

    return speech_text
