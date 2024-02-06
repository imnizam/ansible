#!/usr/bin/env python
import sys
import os
import json
import time
import syslog
import docker
import boto3
import subprocess
import urllib2

def main():
  try:
    sqs_client = boto3.client('sqs',region_name='{{region}}')
    sns_client = boto3.client('sns',region_name='{{region}}')
    scripts_path = sys.path[0]
    info_json = scripts_path+"/info.json"
    while True:
      if not os.path.isfile(info_json):
        time.sleep(5)
      else:
        break

    with open(info_json) as data_file:
        data = json.load(data_file)
    sqs_queue_url = data['sqs_queue_url']
    sns_subscription_arn = data['sns_subscription_arn']
    
    sns_unsubscribe_response = sns_client.unsubscribe(
      SubscriptionArn=sns_subscription_arn
    )
    # queue delete
    sqs_delete_response = sqs_client.delete_queue(
      QueueUrl=sqs_queue_url
    )
  except Exception, e:
    syslog.syslog("ERROR:: Some error occured")

main()