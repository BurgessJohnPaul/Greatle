import boto3


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Greatle_Users')


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

