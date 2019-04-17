from watson_developer_cloud import ToneAnalyzerV3

tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    iam_apikey='Q1OfKtSS5vK9ZqsC_kSNYrRh4_j73ed5h7rb23Ox5QFH',
    url='https://gateway-wdc.watsonplatform.net/tone-analyzer/api'
)


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
