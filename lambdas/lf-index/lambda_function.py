import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

failure = { 'statusCode':500, 'body': 'fail' }

s3 = boto3.client('s3')
client = boto3.client('rekognition')

def write_to_open_search(document):
    print(document)
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    open_search = OpenSearch(
        hosts=[{
            'host': 'search-photos-gw7y52dg2dr66pq6kgf2dhejh4.us-east-1.es.amazonaws.com',
            'port': 443
        }],
        http_auth=AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    open_search.index(index="photos", body=document)

    q = {
        'size': 1000,
        'query': {
            'term': {
                'labels.keyword': 'dog'
            }
        }
    }
    res = open_search.search(index='photos', body=q)['hits']['hits']
    print(res, '*****')
    return True

def detect_labels(photo, bucket):
    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}}, MaxLabels=10)
    recogniton_labels = [label['Name'] for label in response['Labels']]
    return recogniton_labels

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    filename = event['Records'][0]['s3']['object']['key']
    print(f'LF given path {bucket}/{filename}')

    try:
        """
        Get Rekognition labels
        """
        labels = detect_labels(filename, bucket)
        print(f"Labels detected by AI: {len(labels)}", str(labels))
    except Exception as e:
        print(e)
        return failure

    try:
        s3_response = s3.head_object(Bucket=bucket, Key=filename)
        custom_labels = s3_response.get('Metadata', {}).get('x-amz-meta-customlabels', "[]")
        custom_labels_array = json.loads(custom_labels)
        print(f'Custom labels saved for photo: {custom_labels_array}')

        """

        Use the S3 SDK’s headObject method to retrieve the S3 metadata
        created at the object’s upload time.

        Retrieve the x-amz-meta-customLabels metadata field,
        if applicable, and create a JSON array (A1) with the labels.
        & the recognition labels (set of all values)

        Store a JSON object in an OpenSearch index (“photos”)
        that references the S3 object from the PUT event (E1)
        and append string labels to the labels array (A1),
        one for each label detected by Rekognition.

        === format ===

            {
                “objectKey”: “my-photo.jpg”,
                “bucket”: “my-photo-bucket”,
                “createdTimestamp”: “2018-11-05T12:40:02”,
                “labels”: [
                    “person”,
                    “dog”,
                    “ball”,
                    “park”
                ]
            }

        """
        all_labels = [s.lower() for s in labels + custom_labels_array]
        res =  {
                "objectKey": filename,
                "bucket": bucket,
                "createdTimestamp": event['Records'][0]['eventTime'],
                "labels": all_labels
            }

        print(f'Submit the following to opensearch: {res}')

        r = write_to_open_search(res)
        if r:
            return {
                'statusCode':200,
                'body': 'success'
            }
        else:
            return failure

    except Exception as e:
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(filename, bucket))
        return failure