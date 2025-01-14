import random
import re
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
    quotes = re.findall('\^(.*?)_', raw_str)
    return quotes if len(quotes) > 0 else None


def get_passages(raw_list):
    passages = []
    for raw in raw_list:
        quotes = get_quote(re.sub(r'<.*>', '', raw["passage_text"]))
        if quotes is not None:
            [passages.append(quote) for quote in quotes]
    return passages
