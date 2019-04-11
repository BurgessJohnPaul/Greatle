from watson_developer_cloud import DiscoveryV1
from multiprocessing import Process, Pipe
import json
import random

from language_helper import get_passages

ENVIRONMENT = None
COLLECTION = None
ENVIRONMENT_2 = None
COLLECTION_2 = None


def getDiscovery():
    global ENVIRONMENT, COLLECTION
    #joseph's discovery
    ENVIRONMENT = "45b1c136-c499-42dd-be4a-acfe78aede82"
    COLLECTION = "e7d71852-3174-498f-be16-e72f71fb768d"
    return DiscoveryV1(
        version='2018-12-03',
        iam_apikey='QOX9E0nMnTC1aQ9ZMRFGA_Nhnm7QskDQkNapK_sBD_Wj',
        url='https://gateway.watsonplatform.net/discovery/api'
    )


def getDiscovery_2():
    global ENVIRONMENT_2, COLLECTION_2
    #john's discovery
    ENVIRONMENT_2 = "a9e5ef42-6ee3-4b5b-8dbe-ea6c0fce0556"
    COLLECTION_2 = "fc628c92-35e7-4ca1-890c-d515f1ab7b4f"
    return DiscoveryV1(
        version='2018-12-03',
        iam_apikey='Z5qjSJAEOoxr29_cq2AB2YhDasgd0zKkCQAEBvlTdkLf',
        url='https://gateway-wdc.watsonplatform.net/discovery/api'
    )


def query(keywords):
    conn1, conn2 = Pipe(False)
    process = Process(target=query_2, args=[conn2, keywords])
    process.start()
    discovery = getDiscovery()
    query = discovery.query(ENVIRONMENT, COLLECTION, natural_language_query=keywords, return_fields=['Quote', 'Author'])

    if query.get_result()['matching_results'] == 0:
        result = conn1.recv()
        process.join()
        return result

    trainingData = discovery.list_training_data(ENVIRONMENT, COLLECTION)
    queryId = hasQuery(trainingData, keywords)
    if (queryId is None):
        trainQuery = discovery.add_training_data(ENVIRONMENT, COLLECTION, natural_language_query=keywords)
        queryId = trainQuery.get_result()['query_id']
    print(json.dumps(query.get_result(), indent=4))
    print('query id:', queryId)

    result = None
    for result in random.sample(query.get_result()['results'], min(10, query.get_result()['matching_results'])):
        print(result['Quote'])
        docId = result['id']

        examples = discovery.list_training_examples(ENVIRONMENT, COLLECTION, queryId)

        if(hasDocument(examples, docId)):
            trainingExample = discovery.get_training_example(ENVIRONMENT, COLLECTION, queryId, docId)
            relevance = trainingExample.get_result()['relevance']
            print(trainingExample.get_result()['relevance'])
            print('relevance:', relevance)
            if relevance > 0:
                break
        else:
            break

    process.join()
    return None if result is None else(result['Quote'], result['id'], queryId, result['Author'])


def query_2(conn, keywords):
    discovery = getDiscovery_2()
    query = discovery.query(ENVIRONMENT_2, COLLECTION_2, natural_language_query=keywords, passages=True, passages_characters=350, passages_count=7)
    result = None
    if(query.get_result()['matching_results'] > 0):
        sentences = get_passages(query.get_result()["passages"])
        if len(sentences) > 0:
            result = sentences[random.randint(0, len(sentences) - 1)]
    conn.send(None if result is None else result)
    conn.close()


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
