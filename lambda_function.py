#!/usr/bin/env python

'''
usage:
    pip install -t . elasticsearch-curator requests-aws4auth
    zip -r ../upload.zip *

Lambda Role:
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

Amazon ES Access Policy:
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
'''

import uuid
import boto3
import curator
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection


class Job(object):
    def __init__(self, endpoint, prefix, retention_days):
        self._endpoint = endpoint
        self._prefix = prefix
        self._retention_days = retention_days

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def prefix(self):
        return self._prefix

    @property
    def retention_days(self):
        return self._retention_days

    def __str__(self):
        return '{ %s, %s, %d }' % (self._endpoint, self._prefix, self._retention_days,)


_JOBS = [
    Job('search-xxxx-xxxxxxxxxxxx.your-region.es.amazonaws.com', 'logstash-', 30)
]
_REGION = 'your-region'
_ROLE_ARN = 'arn:aws:iam::xxxxxxxxxxxx:role/your-lambda-role'


def lambda_handler(event, context):
    ''' entrypoint '''
    for job in _JOBS:
        print 'start job: %s' % (job,)
        clean(job)
        print 'end job: %s' % (job,)


def clean(job):
    '''
    :param job: class:`Job`
    '''
    access_key, secret_key, token = get_credential()

    awsauth = AWS4Auth(
        access_key,
        secret_key,
        _REGION,
        'es',
        session_token=token
    )

    es = Elasticsearch(
        hosts=[{'host': job.endpoint, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    run_curator(es, job.prefix, job.retention_days)


def get_credential():
    '''
    :return: (access_key, secret_key, token,)
    '''
    sts_client = boto3.client('sts')
    assume_role = sts_client.assume_role(
        RoleArn=_ROLE_ARN,
        RoleSessionName='role-session-%s' % (uuid.uuid4().hex,)
    )
    credentials = assume_role['Credentials']

    return (credentials['AccessKeyId'], credentials['SecretAccessKey'], credentials['SessionToken'],)


def run_curator(es, prefix, retention_days):
    '''
    :param es: class:`elasticsearch.Elasticsearch`
    :param prefix: like "logstash-".
    :param retention_days: days for retaining indexes.
    '''
    indices = curator.IndexList(es)
    print 'all indices: %s' % (indices.all_indices,)

    indices.filter_by_regex(kind='prefix', value=prefix)
    indices.filter_by_age(source='creation_date', direction='older', unit='days', unit_count=retention_days)
    print 'filtered indices: %s' % (indices.indices,)

    if indices.indices:
        delete_indices = curator.DeleteIndices(indices)
        delete_indices.do_action()


if __name__ == '__main__':
    lambda_handler(None, None)
