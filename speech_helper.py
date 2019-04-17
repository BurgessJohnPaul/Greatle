from ask_sdk_model import ui
from ask_sdk_model.interfaces.display import RenderTemplateDirective, BodyTemplate7, BackButtonBehavior, ImageInstance, \
    Image, ImageSize
from ask_sdk_model.ui import SimpleCard, StandardCard
import dynamo_helper


def build_response(handler_input, card_title, card_text, speech_text, card_image_url=None, end_session=False):
    if handler_input.attributes_manager.session_attributes["drunk_mode_state"]:
        speech_text = '<prosody rate="x-slow"><emphasis level="strong">' + speech_text + '</emphasis></prosody>'

    if card_image_url and supports_display(handler_input):
        card = StandardCard(card_title, card_text, ui.Image(card_image_url, card_image_url))
        img = Image('Meme', [ImageInstance(url=card_image_url, size=ImageSize.X_SMALL)])
        directive = RenderTemplateDirective(
                    BodyTemplate7(
                        back_button=BackButtonBehavior.HIDDEN,
                        image=img, title=card_title))
        handler_input.response_builder.speak(speech_text).set_card(card).add_directive(directive).set_should_end_session(end_session)
    else:
        card = SimpleCard(card_title, card_text)
        handler_input.response_builder.speak(speech_text).set_card(card).set_should_end_session(end_session)

    return handler_input.response_builder.response


def supports_display(handler_input):
    # type: (HandlerInput) -> bool
    """Check if display is supported by the skill."""
    try:
        if hasattr(
                handler_input.request_envelope.context.system.device.
                        supported_interfaces, 'display'):
            return (
                    handler_input.request_envelope.context.system.device.
                    supported_interfaces.display is not None)
    except:
        return False



def set_drunk_mode(user_id, handler_input, state):
    dynamo_helper.set_col_val(user_id, "drunk_mode_state", state)
    handler_input.attributes_manager.session_attributes["drunk_mode_state"] = state


def get_drunk_mode_state(user_id):
    response = dynamo_helper.get_item_from_users(user_id)
    if 'Item' in response and 'drunk_mode_state' in response['Item']:
        return response['Item']['drunk_mode_state']
    else:
        return False
