import json
import boto3
import os
from botocore.exceptions import ClientError
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# opensearch query
def query(keyword):
    print('opensearch', keyword)
    q = {
        'size': 1000,
        'query': {
            'term': {
                'labels': {
                    'value': keyword.lower()
                }
            }
        }
    }

    es_client = boto3.client('opensearch')
    host = es_client.describe_domain(DomainName='photos')['DomainStatus']['Endpoint']

    client = OpenSearch(
        hosts=[{
            'host': 'search-photos-gw7y52dg2dr66pq6kgf2dhejh4.us-east-1.es.amazonaws.com', #'search-photos-gw7y52dg2dr66pq6kgf2dhejh4.us-east-1.es.amazonaws.com'
            'port': 443
        }],
        http_auth=get_awsauth('us-east-1', 'es'),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    res = client.search(index='photos', body=q) #{"query": {"match": {"_all": keyword}}})
    resi = res['hits']['hits']
    print('opensearch returned', resi)
    results = []
    for hit in resi:
        results.append(hit['_source']['objectKey'])

    print('request returning', results)
    return results

def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)


client = boto3.client('lexv2-runtime')
def lambda_handler(event, context):

    print('event', event)
    try:
        text_for_lex = event['q']
        if text_for_lex[-1].lower() == 's':
            text_for_lex = text_for_lex[:-1]
        # print(text_for_lex)
    except:
        return []

    # Initiate conversation with Lex
    response = client.recognize_text(
            botId='ZAW9ZHRNXB',
            botAliasId='MPCLEYXZ6Y',
            localeId='en_US',
            sessionId='testuser',
            text=text_for_lex)

    msg_from_lex = response.get('sessionState', [])

    if msg_from_lex:
        try:
            queries = msg_from_lex['intent']['slots']
            q1 = queries['query1']['value']['interpretedValue']
            q2 = queries['query2']['value']['interpretedValue']
        except:
            return []

    result = query(json.dumps(q1))
    print('result', result)
    return result
