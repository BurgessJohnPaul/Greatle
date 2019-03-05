import random
from difflib import SequenceMatcher


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def get_most_similar_string(goal_string, string_list):
    best_string = "@"
    similarity_value = similar(best_string, goal_string)
    for s in string_list:
        if similar(s, goal_string) > similarity_value:
            best_string = s
            similarity_value = similar(best_string, goal_string)
    return best_string, similarity_value


def get_quote(raw_str):
    is_quote = lambda quote: '#' not in quote and '@' not in quote and quote is not ''
    quotes = list(filter(is_quote, [raw.strip() for raw in raw_str.split('^')]))
    return quotes[random.randint(0, len(quotes) - 1)] if len(quotes) > 0 else None
