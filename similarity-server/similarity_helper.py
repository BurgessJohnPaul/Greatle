import requests

# ---
# Returns the semantic similarity between str1 and str2 as a decimal between 0 and 1
# ---
def get_similarity(str1, str2):
    try:
        data = {'phrase1': str1, 'phrase2': str2}
        response = requests.get('http://127.0.0.1:5000/gs', data=data)
        return response.content
    except Exception:
        return None

# ---
# Returns the similarity of a phrase to a list of phrases
# ---
def match_similarity_with_list(new_phrase, phrase_list):
    try:
        l = [(phrase, get_similarity(new_phrase, phrase)) for phrase in phrase_list]
        l = sorted(l, key=lambda x:x[1], reverse=True)
        return l
    except Exception:
        return None


x = match_similarity_with_list('that big truck over there', ['big fat cat', 'fat chungus'])
print(x)