from ask_sdk_model.ui import SimpleCard
import dynamo_helper


def build_response(handler_input, card_title, card_text, speech_text, end_session=False):
    if handler_input.attributes_manager.session_attributes["drunk_mode_state"] == "True":
        speech_text = '<prosody rate="x-slow"><emphasis level="strong">' + speech_text + '</emphasis></prosody>'

    handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard(card_title, card_text)).set_should_end_session(
        end_session)

    return handler_input.response_builder.response


def set_drunk_mode(user_id, handler_input, state):
    dynamo_helper.set_col_val(user_id, "drunk_mode_state", str(state))
    handler_input.attributes_manager.session_attributes["drunk_mode_state"] = str(state)


def get_drunk_mode_state(user_id):
    response = dynamo_helper.get_item_from_users(user_id)
    if 'Item' in response and 'drunk_mode_state' in response['Item']:
        print("Drunk Mode State: " + response['Item']['drunk_mode_state'])
        print("Drunk Mode State Type: ", type(response['Item']['drunk_mode_state']))
        print("Drunk Mode is True: ", response['Item']['drunk_mode_state'] == "True")
        return response['Item']['drunk_mode_state'] == "True"
    else:
        return False
