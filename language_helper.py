from difflib import SequenceMatcher


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def get_most_similar_string(goal_string, string_list ):
    best_string = "@"

    for s in string_list:
        if similar(s, goal_string) > similar(best_string, goal_string):
            best_string = s
    return best_string

