import json
import boto3

lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    if event['httpMethod'] == 'POST':
        payload = event['body']

        print(event['headers'])
        print(event['queryStringParameters'])

        if('Content-Type' in event['headers']):
            content_type = event['headers']['Content-Type']
        elif('content-type' in event['headers']):
            content_type = event['headers']['content-type']
        else:
            content_type = None

        endpoint_name = event['queryStringParameters']['endpoint_name']
        infer_type = event['queryStringParameters']['infer_type'] if('infer_type' in event['queryStringParameters']) else 'sync'
        keywords = json.loads(event['queryStringParameters']['keywords']) if('keywords' in event['queryStringParameters']) else None

        body = {
            "endpoint_name": endpoint_name,
            "content_type": content_type,
            "payload": payload,
            "infer_type": infer_type
        }
        
        response = lambda_client.invoke(
            FunctionName = 'industry_ai_invoke_endpoint',
            InvocationType = 'RequestResponse',
            Payload = json.dumps(body)
        )

        if('FunctionError' not in response):
            payload = response["Payload"].read().decode("utf-8")
            payload = json.loads(payload)
            print(payload['body'])

            return {
                'statusCode': payload['statusCode'],
                'body': payload['body']
            }
        else:
            return {
                'statusCode': 400,
                'body': response["FunctionError"]
            }
        
    else:
        return {
            'statusCode': 400,
            'body': "Unsupported HTTP method"
        }
