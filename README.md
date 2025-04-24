# Semi-Naive Datalog over AWS Step Function (LocalStack Demo)

This project demonstrates how to simulate a semi-naïve Datalog evaluation engine
using AWS Lambda, Step Functions, and S3 — all locally using LocalStack.

---

## Goal
Simulate incremental Datalog rule evaluation with partitioned parallelism using:
- evaluate_partition.py: A Lambda function that runs inference on one partition
- merge_results.py: A Lambda function that merges output and checks fixpoint
- S3: Storage for all inputs/outputs
- Step Function: Drives the iteration until fixpoint

---

## Setup

### 1. Install LocalStack & Tools
```bash
pip install localstack awscli awslocal
localstack start
```

### 2. Package Lambda Functions
```bash
cd src/
zip -r evaluate_partition.zip evaluate_partition.py
zip -r merge_results.zip merge_results.py
```

### 3. Create S3 Bucket
```bash
awslocal s3 mb s3://my-datalog-bucket
```
Upload the following example files:
- edges.json
- reach_all.json
- delta_round_0.json

### 4. Create Lambda Functions
```bash
awslocal lambda create-function \
  --function-name evaluate_partition \
  --runtime python3.9 \
  --role arn:aws:iam::000000000000:role/lambda-role \
  --handler evaluate_partition.lambda_handler \
  --zip-file fileb://evaluate_partition.zip

awslocal lambda create-function \
  --function-name merge_results \
  --runtime python3.9 \
  --role arn:aws:iam::000000000000:role/lambda-role \
  --handler merge_results.lambda_handler \
  --zip-file fileb://merge_results.zip
```

### 5. Create Step Function
Convert the Step Function YAML definition into JSON (definition.json).
```bash
awslocal stepfunctions create-state-machine \
  --name SemiNaiveDatalog \
  --role-arn arn:aws:iam::000000000000:role/stepfunction-role \
  --definition file://definition.json
```

---

## Run Execution

Prepare your input.json:
```json
{
  "bucket": "my-datalog-bucket",
  "num_partitions": 2,
  "delta_key": "delta_round_0.json",
  "edge_key": "edges.json",
  "reach_key": "reach_all.json",
  "next_delta_key": "delta_round_1.json",
  "partitions": [
    { "partition_id": 0, "output_key": "delta_part_0.json" },
    { "partition_id": 1, "output_key": "delta_part_1.json" }
  ]
}
```

Start the execution:
```bash
awslocal stepfunctions start-execution \
  --state-machine-arn arn:aws:states:us-east-1:000000000000:stateMachine:SemiNaiveDatalog \
  --input file://input.json
```

---

## Submit
- Your Lambda source files
- JSON input files used
- A screenshot or command result showing output or execution history

If you get stuck, share your error message or stack trace.

---

Once this works, you're ready to scale and test real workloads.

