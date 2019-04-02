from watson_developer_cloud import DiscoveryV1
import json

ENVIRONMENT = None
COLLECTION = None

def getDiscovery():
    global ENVIRONMENT, COLLECTION
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
    ENVIRONMENT = "45b1c136-c499-42dd-be4a-acfe78aede82"
    COLLECTION = "e7d71852-3174-498f-be16-e72f71fb768d"
    return DiscoveryV1(
        version='2018-12-03',
        iam_apikey='QOX9E0nMnTC1aQ9ZMRFGA_Nhnm7QskDQkNapK_sBD_Wj',
        url='https://gateway.watsonplatform.net/discovery/api'
    )


def query(keywords):
    discovery = getDiscovery()
    query = discovery.query(ENVIRONMENT, COLLECTION, natural_language_query=keywords, passages=True,
                            passages_fields='Quote')

    trainingData = discovery.list_training_data(ENVIRONMENT, COLLECTION)
    queryId = hasQuery(trainingData, keywords)
    if(queryId is None):
        trainQuery = discovery.add_training_data(ENVIRONMENT, COLLECTION, natural_language_query=keywords)
        queryId = trainQuery.get_result()['query_id']
    print(json.dumps(query.get_result(), indent=4, sort_keys=True))
    return query, queryId

def hasQuery(trainingData, word):
    for query in trainingData.get_result()['queries']:
        if(query['natural_language_query']==word):
            return query['query_id']
    return None

def hasDocument(examples, documentId):
    for example in examples.get_result()['examples']:
        if(example['document_id']==documentId):
            return True
    return False

def rateQuery(queryId, docId, relevant=True):
    discovery = getDiscovery()

    examples = discovery.list_training_examples(ENVIRONMENT, COLLECTION, queryId)
    if(not hasDocument(examples, docId)):
        relevance = 10 if relevant else 0
        discovery.create_training_example(ENVIRONMENT, COLLECTION, queryId, document_id=docId, relevance=relevance)
