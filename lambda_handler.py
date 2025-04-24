# AWS Lambda using S3 for input/output
import json
import hashlib
import boto3

s3 = boto3.client("s3")

def partition_key(x, num_partitions=2):
    return int(hashlib.md5(x.encode()).hexdigest(), 16) % num_partitions

def load_json(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(obj['Body'].read().decode())

def save_json(bucket, key, data):
    s3.put_object(Bucket=bucket, Key=key, Body=json.dumps(data))

def lambda_handler(event, context):
    bucket = event['bucket']
    partition_id = event['partition_id']
    delta_key = event['delta_key']
    edge_key = event['edge_key']
    reach_key = event['reach_key']
    output_key = event['output_key']
    num_partitions = event.get('num_partitions', 2)

    delta_reach = set(map(tuple, load_json(bucket, delta_key)))
    edge_facts = set(map(tuple, load_json(bucket, edge_key)))
    reach_all = set(map(tuple, load_json(bucket, reach_key)))

    new_facts = set()
    for x, y in delta_reach:
        if partition_key(x, num_partitions) != partition_id:
            continue
        for y2 in [z for a, z in edge_facts if a == y]:
            if (x, y2) not in reach_all:
                new_facts.add((x, y2))

    save_json(bucket, output_key, list(new_facts))

    return {
        'statusCode': 200,
        'body': json.dumps({
            "partition_id": partition_id,
            "new_facts_count": len(new_facts),
            "output_key": output_key
        })
    }


