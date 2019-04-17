import random
import dynamo_helper
import sentiment_helper

joy_responses = ["That's great!", "It sounds like you had a good day.", "Wow that's awesome.", "I am happy for you."]
sadness_responses = ["That's too bad.", "Tomorrow's another day.", "I'm sorry you don't feel great",
                     "It's okay to feel sad sometimes"]
default_responses = ["Okay, I've recorded this in your journal"]

def create_journal_helper(user_id, slots):
    if slots is None or "JournalEntry" not in slots:
        speech_text = "I have no idea what is going on with these journal slots today please send help"
    else:
        journal_entry = slots['JournalEntry'].value

        dynamo_helper.create_journal_entry(user_id, journal_entry)

        sentiments = sentiment_helper.get_sentiment(journal_entry)

        if "Joy" in sentiments:
            speech_text = random.choice(joy_responses)
        elif "Anger" in sentiments or "Sadness" in sentiments:
            speech_text = random.choice(sadness_responses)
        else:
            speech_text = random.choice(default_responses)

    return speech_text


def get_random_journal_entry_helper(user_id):

    journal_list = dynamo_helper.get_journal(user_id)

    if len(journal_list) == 0:
        speech_text = "You don't have any journal entries. Say 'I'd like to journal' to add a new entry"
    else:
        random_entry = random.choice(journal_list)
        speech_text = random_entry["text"]

    return speech_text


def get_all_entries(user_id):
    journal_list = dynamo_helper.get_journal(user_id)

    if len(journal_list) == 0:
        return []
    else:
        return journal_list


