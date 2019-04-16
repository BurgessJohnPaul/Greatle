import dynamo_helper


def create_journal_helper(user_id, slots):
    if slots is None or "JournalEntry" not in slots:
        speech_text = "I have no idea what is going on with these journal slots today please send help"
    else:
        journal_entry = slots['JournalEntry'].value

        dynamo_helper.create_journal_entry(user_id, journal_entry)

        speech_text = "Update this to say something depending on the sentiment of the entry."

    return speech_text
