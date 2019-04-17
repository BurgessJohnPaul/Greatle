import random
import dynamo_helper


def create_journal_helper(user_id, slots):
    if slots is None or "JournalEntry" not in slots:
        speech_text = "I have no idea what is going on with these journal slots today please send help"
    else:
        journal_entry = slots['JournalEntry'].value

        dynamo_helper.create_journal_entry(user_id, journal_entry)

        speech_text = "Update this to say something depending on the sentiment of the entry."

    return speech_text


def get_random_journal_entry_helper(user_id):

    journal_list = dynamo_helper.get_journal(user_id)

    if len(journal_list) == 0:
        speech_text = "You don't have any journal entries. Say 'I'd like to journal' to add a new entry"
    else:
        random_entry = random.choice(journal_list)
        speech_text = random_entry["text"]

    return speech_text

