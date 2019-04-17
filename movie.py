import json
import csv

from watson_developer_cloud import ToneAnalyzerV3

tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    iam_apikey='Q1OfKtSS5vK9ZqsC_kSNYrRh4_j73ed5h7rb23Ox5QFH',
    url='https://gateway-wdc.watsonplatform.net/tone-analyzer/api'
)

# with open('tv.txt', 'r') as myfile:
#     data = myfile.read().replace('\n', '').replace('-', '')
import csv
dictionary = {}
pretty = {'Joy': 'joyful', 'Fear': 'fearful', 'Sadness': 'sad', 'Anger': 'angry', 'Tentative': 'tentative',
                  'Analytical': 'analytical', 'Confident': 'confident'}
somewhat_prefix = 'somewhat '

with open('the-office-lines - scripts.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            line_count += 1
            key = "" + row[1] + ":" + row[2] + ":" + row[5]
            if key in dictionary:
                dictionary[key] = dictionary[key] + row[4]
            else:
                dictionary[key] = row[4]
tone_analysis = tone_analyzer.tone(
            {'text': dictionary["1:1:Jim"]},
            'application/json',
            sentences=False
        ).get_result()
tones = [(pretty[str(tone['tone_name'])], tone['score']) for tone in tone_analysis['document_tone']['tones']]
pretty_tones = []
for tone in tones:
    if tone[1] < 0.75:
        pretty_tones.append(somewhat_prefix + tone[0])
    else:
        pretty_tones.append(tone[0])
pretty_tones_str = str(pretty_tones).replace('\'', '').replace('[', '').replace(']', '')
pretty_str = 'Tone is ' + pretty_tones_str + '.'

print(pretty_str)
# while(True):
#     season = input("Enter a season: ")
#     episode = input("Enter an episode: ")
#     name = input("Enter a character: ")
#     key = "" + str(season) + ":" + str(episode) + ":" + str(name)
#     if not key in dictionary:
#         print("Try again loser")
#     else:
#         tone_analysis = tone_analyzer.tone(
#             {'text': dictionary[key]},
#             'application/json',
#             sentences=False
#         ).get_result()
#         tones = [(pretty[str(tone['tone_name'])], tone['score']) for tone in tone_analysis['document_tone']['tones']]
#         pretty_tones = []
#         for tone in tones:
#             if tone[1] < 0.75:
#                 pretty_tones.append(somewhat_prefix + tone[0])
#             else:
#                 pretty_tones.append(tone[0])
#         pretty_tones_str = str(pretty_tones).replace('\'', '').replace('[', '').replace(']', '')
#         pretty_str = name + '\'s tone is ' + pretty_tones_str + '.'
#         print(tones)
#         print(pretty_str)
#         # print(json.dumps(tone_analysis, indent=2))
#
# # text = str(data)
# # tone_analysis = tone_analyzer.tone(
# #     {'text': text},
# #     'application/json'
# # ).get_result()
# # tones = [(str(tone['tone_name']), tone['score']) for tone in tone_analysis['document_tone']['tones']]
# # print(tones)
