from watson_developer_cloud import DiscoveryV1
import json

environment_id = None
collection_id = None

def getDiscovery():
    global environment_id, collection_id
    '''
    #john's discovery
    environment_id = "a9e5ef42-6ee3-4b5b-8dbe-ea6c0fce0556"
    collection_id = "71f0df80-85e0-48f5-bc76-b5d9eac1ac9e"
    return DiscoveryV1(
        version='2018-12-03',
        iam_apikey='Z5qjSJAEOoxr29_cq2AB2YhDasgd0zKkCQAEBvlTdkLf',
        url='https://gateway-wdc.watsonplatform.net/discovery/api'
    )
    '''
    #joseph's discovery
    environment_id = "45b1c136-c499-42dd-be4a-acfe78aede82"
    collection_id = "e7d71852-3174-498f-be16-e72f71fb768d"
    return DiscoveryV1(
        version='2018-12-03',
        iam_apikey='QOX9E0nMnTC1aQ9ZMRFGA_Nhnm7QskDQkNapK_sBD_Wj',
        url='https://gateway.watsonplatform.net/discovery/api'
    )


def query(keywords):
    discovery = getDiscovery()
    query = discovery.query(environment_id, collection_id, natural_language_query=keywords, passages=True,
                            passages_characters=500)
    print(json.dumps(query.get_result(), indent=4, sort_keys=True))
    return query
