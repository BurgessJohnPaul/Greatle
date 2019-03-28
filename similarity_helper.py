import requests


# ---
# Returns the semantic similarity between str1 and str2 as a decimal between 0 and 1
# ---
def get_similarity(str1, str2):
    try:
        data = {'phrase1': str1, 'phrase2': str2}
        response = requests.get('https://greatle.localtunnel.me/gs', data=data)
        return response.content
    except Exception as e:
        print('Similarity helper error:')
        print(e)
        return None


# ---
# Returns the similarity of a phrase to a list of phrases
# ---
def match_similarity_with_list(new_phrase, phrase_list):
    try:
        l = [(phrase, get_similarity(new_phrase, phrase)) for phrase in phrase_list]
        l = sorted(l, key=lambda x:x[1], reverse=True)
        return l
    except Exception as e:
        print('Similarity helper error:')
        print(e)
        return None


# Example
if __name__ == '__main__':
    print(match_similarity_with_list('taco', ['big taco', 'big cat']))
