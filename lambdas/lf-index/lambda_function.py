import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

s3 = boto3.client('s3')
client = boto3.client('rekognition')

def write_to_open_search(document):
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
    return True

def detect_labels(photo, bucket):
    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}}, MaxLabels=10)
    recogniton_labels = [label["Name"] for label in response['Labels']]
    return recogniton_labels

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    print(bucket, key)

    try:
        labels = detect_labels(key, bucket)
        print(f"Labels detected: {len(labels)}", str(labels))
        """
        Get Rekognition labels
        """
    except Exception as e:
        print(e)

    try:
        # response = s3.get_object(Bucket=bucket, Key=key)
        s3_response = s3.head_object(Bucket=bucket, Key=key)
        custom_labels = s3_response.get('Metadata', {}).get('x-amz-meta-customlabels', "[]")
        custom_labels_array = json.loads(custom_labels)
        print(custom_labels_array)
        print("CONTENT TYPE: " + s3_response['ContentType'])

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
                "objectKey": key,
                "bucket": bucket,
                "createdTimestamp": event['Records'][0]['eventTime'],
                "labels": all_labels
            }
        print(res)

        r = write_to_open_search(res)
        if r:
            return {
                'statusCode':200,
                'body': all_labels
            }
        else:
            return {
                'statusCode':500,
                'body': json.dumps([])
            }

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

