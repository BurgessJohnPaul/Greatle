from watson_developer_cloud import ToneAnalyzerV3

tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    iam_apikey='Q1OfKtSS5vK9ZqsC_kSNYrRh4_j73ed5h7rb23Ox5QFH',
    url='https://gateway-wdc.watsonplatform.net/tone-analyzer/api'
)

HAPPY = "HAPPY"
SLIGHTLY_HAPPY = "SLIGHTLY_HAPPY"
NEUTRAL = "NEUTRAL"
SLIGHTLY_SAD = "SLIGHTLY_SAD"
SAD = "SAD"
JOY_TONE = 'Joy'
ANGER_TONE = 'Anger'
SAD_TONE = 'Sad'



def get_sentiment_and_degree(text):
    tone_analysis = tone_analyzer.tone(
     {'text': text},
     'application/json'
    ).get_result()
    tones = [(str(tone['tone_name']), tone['score']) for tone in tone_analysis['document_tone']['tones']]
    print ("Text: ", text)
    print ("Tones: ", tones)
    #Returns a list of tuples: (sentiment, degree)
    return tones


def get_sentiment(text):
    tones = get_sentiment_and_degree(text)

    sentiment = []
    for feeling_value in tones:
        sentiment.append(feeling_value[0])
    #Returns a list of just the sentiments detected
    return sentiment


def sentiment_with_threshold(text):
    tone_analysis = tone_analyzer.tone(
        {'text': text},
        'application/json'
    ).get_result()
    tones = [(str(tone['tone_name']), tone['score']) for tone in tone_analysis['document_tone']['tones']]

    for tone in tones:
        if tone[0] == JOY_TONE:
            if tone[1] > .8:
                return HAPPY
            else:
                return SLIGHTLY_HAPPY
        if tone[0] == SAD_TONE or ANGER_TONE:
            if tone[1] > .8:
                return SAD
            else:
                return SLIGHTLY_SAD

    return NEUTRAL
