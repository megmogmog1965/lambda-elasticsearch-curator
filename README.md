# lambda-elasticsearch-curator

## What's this ?

[AWS Lambda] function to run [elasticsearch-curator] for [Amazon ES].

## How to use

Edit ``lambda_function.py``.

```python
_JOBS = [
    Job('search-xxxx-xxxxxxxxxxxx.your-region.es.amazonaws.com', 'logstash-', 30)
]
_REGION = 'your-region'
_ROLE_ARN = 'arn:aws:iam::xxxxxxxxxxxx:role/your-lambda-role'
```

Create zipped function. Upload it as ``Python 2.7`` [AWS Lambda] function.

```
pip install -t . elasticsearch-curator requests-aws4auth
zip -r ../upload.zip *
```

You need to add following permission to IAM role for [AWS Lambda] execution.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:*:*:*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "es:ESHttpGet",
            "Resource": "arn:aws:es:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": "es:ESHttpPost",
            "Resource": "arn:aws:es:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": "es:ESHttpDelete",
            "Resource": "arn:aws:es:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "*"
        }
    ]
}
```

And access policy for [Amazon ES].

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



[AWS Lambda]:https://aws.amazon.com/lambda
[Amazon ES]:https://aws.amazon.com/elasticsearch-service/
[elasticsearch-curator]:https://www.elastic.co/guide/en/elasticsearch/client/curator/current/index.html
