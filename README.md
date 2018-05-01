# lambda-elasticsearch-curator

## What's this ?

AWS Lambda function to run elasticsearch-curator for Amazon ES.

## How to use

Edit ``lambda_function.py``.

```python
_JOBS = [
    Job('search-xxxx-xxxxxxxxxxxx.your-region.es.amazonaws.com', 'logstash-', 30)
]
_REGION = 'your-region'
_ROLE_ARN = 'arn:aws:iam::xxxxxxxxxxxx:role/your-lambda-role'
```

Create zipped function. Upload it.

```
pip install -t . elasticsearch-curator requests-aws4auth
zip -r ../upload.zip *
```

You need to add following permission to IAM role for lambda execution.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Resource": "*",
            "Effect": "Allow"
        }
    ]
}
```

And access policy for Amazon ES.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::xxxxxxxxxxxx:role/your-lambda-role"
            },
            "Action": "es:*",
            "Resource": "arn:aws:es:your-region:xxxxxxxxxxxx:domain/your-domain/*"
        }
    ]
}
```
