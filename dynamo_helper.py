import boto3
from difflib import SequenceMatcher

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Greatle_Users')


def get_row(user_id):
    response = table.get_item(
        Key={
            'user_id': user_id
        }
    )
    return response

def set_col_val(user_id, col, val):
    table.update_item(
        Key={
            'user_id': user_id
        },
        UpdateExpression='SET ' + col + ' = :val1',
        ExpressionAttributeValues={
            ':val1': val
        }
    )


def get_item_from_users(user_id):
    return table.get_item(
        Key={
            'user_id': user_id
        }
    )


def put_item_to_users(user_id):
    table.put_item(
        Item={
            'user_id': user_id
        }
    )


def update_name_from_users(user_id, users_name):
    table.update_item(
        Key={
            'user_id': user_id
        },
        UpdateExpression='SET user_name = :val1',
        ExpressionAttributeValues={
            ':val1': users_name
        }
    )


def update_age_from_users(user_id, age):
    table.update_item(
        Key={
            'user_id': user_id
        },
        UpdateExpression='SET age = :val1',
        ExpressionAttributeValues={
            ':val1': age
        }
    )


def list_goals(user_id):
    return list_goals_with_status(user_id, "ACTIVE")


def list_goals_with_status(user_id, status):
    response = get_row(user_id)

    desc_list = []

    #Return empty list if no 'goal_list'
    if 'goal_list' in response['Item']:
        goals = response['Item']['goal_list']
        for goal in goals:
            if (goal["status"] == status):
                desc_list.append(goal["description"])
    return desc_list


def update_goal_status(user_id, goal_desc, status):
    response = get_row(user_id)

    goals = response['Item']['goal_list']
    for goal in goals:
        if goal["description"] == goal_desc:
            goal["status"] = status

    set_col_val(user_id, 'goal_list', goals)


def delete_goal(user_id, goal_desc):
    response = get_row(user_id)

    goals = response['Item']['goal_list']
    for goal in goals:
        if goal["description"] == goal_desc:
            goals.remove(goal)

    set_col_val(user_id, 'goal_list', goals)


def create_goal(user_id, goal_desc, created_on, complete_by):
    response = get_row(user_id)

    if "goal_list" not in response["Item"]:
        response['Item']['goal_list'] = []

    goals = response['Item']['goal_list']

    new_goal = {}
    new_goal["description"] = goal_desc
    new_goal["created_on"] = created_on
    new_goal["complete_by"] = complete_by
    new_goal["status"] = "ACTIVE"

    goals.append(new_goal)

    set_col_val(user_id, 'goal_list', goals)

