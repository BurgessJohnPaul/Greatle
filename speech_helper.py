from ask_sdk_model.ui import SimpleCard
drunk_mode_active = False


def build_response(handler_input, card_title, speech_text, end_session):
    if drunk_mode_active:
        speech_text = '<prosody rate="x-slow"><emphasis level="strong">' + speech_text + '</emphasis></prosody>'

    handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard(card_title, speech_text)).set_should_end_session(
        end_session)

    return handler_input.response_builder.response
