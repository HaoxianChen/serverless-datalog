# Lambda that merges outputs and checks fixpoint

import json
import boto3

s3 = boto3.client("s3")

def load_json(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(obj['Body'].read().decode())

def lambda_handler(event, context):
    bucket = event['bucket']
    result_keys = event['result_keys']

    all_new_facts = set()
    for key in result_keys:
        new_facts = set(map(tuple, load_json(bucket, key)))
        all_new_facts |= new_facts

    has_new_delta = len(all_new_facts) > 0
    merged_key = event.get('merged_output_key', 'merged_delta.json')

    s3.put_object(Bucket=bucket, Key=merged_key, Body=json.dumps(list(all_new_facts)))

    return {
        "merged_output_key": merged_key,
        "has_new_delta": has_new_delta,
        "new_facts_count": len(all_new_facts)
    }

