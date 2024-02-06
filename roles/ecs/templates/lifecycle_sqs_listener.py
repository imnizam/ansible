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

ec2_client = boto3.client('ec2',region_name='{{region}}')
ecs_client = boto3.client('ecs',region_name='{{region}}')
asg_client = boto3.client('autoscaling',region_name='{{region}}')
docker_client = docker.from_env()
sqs_client = boto3.client('sqs',region_name='{{region}}')
sns_client = boto3.client('sns',region_name='{{region}}')

def destroy():
  try:
    ecs_host_data = urllib2.urlopen('http://localhost:51678/v1/metadata').read()
    data = json.loads(ecs_host_data)
    cluster = data["Cluster"]
    instance_arn = data["ContainerInstanceArn"]

    syslog.syslog("Starting drain!")
    drain_response = ecs_client.update_container_instances_state(
      cluster=cluster,
      containerInstances=[instance_arn],
      status='DRAINING'
    )
    lc_response = asg_client.describe_lifecycle_hooks(
      AutoScalingGroupName="{{nuproj_instance_facts.tags['aws:autoscaling:groupName']}}"
    )
    heartbeat_timeout = lc_response['LifecycleHooks'][0]['HeartbeatTimeout']
    drain_wait_timeout = int(heartbeat_timeout * 0.80)
    every = 20
    i = 0
    while i < drain_wait_timeout:
      syslog.syslog("Containers yet to be drained="+str(len(docker_client.containers.list())))
      if len(docker_client.containers.list()) > 1:
        time.sleep(every)
        i = i + every
      else:
        break
    deregister_response = ecs_client.deregister_container_instance(
      cluster=cluster,
      containerInstance=instance_arn,
      force=True
    )
    subprocess.check_output("systemctl stop datadog-agent.service" , shell=True)
    subprocess.check_output("systemctl stop ecs_agent.service" , shell=True)

    containers = docker_client.containers.list()
    for container in containers:
      container.stop(timeout=45)
  except Exception, e:
    syslog.syslog("Error:: Problem occured in drain and deregistering.")


def main():
  try:
    scripts_path = sys.path[0]
    host_instance_id = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read()

    queue_name = "{{consul_data.Environment}}-nuproj-ecs-asg-lifecycle-target-" + host_instance_id
    sns_topic_arn = "{{consul_data['Hostname']['SNSTopicARN']}}"
    sqs_queue_create = sqs_client.create_queue(
      QueueName=queue_name,
      Attributes={
          "Policy" : "{ \"Version\": \"2012-10-17\", \"Statement\": [{ \"Sid\": \"Sid1472714724390\", \"Effect\": \"Allow\", \"Principal\": { \"AWS\": \"*\" }, \"Action\": \"SQS:SendMessage\", \"Resource\": \"*\", \"Condition\": { \"ArnEquals\": { \"aws:SourceArn\": \"{{consul_data['Hostname']['SNSTopicARN']}}\" } } } ] }"
      }
    )

    sqs_queue_url = sqs_queue_create["QueueUrl"]
    sqs_get_arn = sqs_client.get_queue_attributes(
      QueueUrl=sqs_queue_url,
      AttributeNames=[
          'QueueArn'
      ]
    )
    sqs_queue_arn = sqs_get_arn["Attributes"]["QueueArn"]
    sns_subscribe = sns_client.subscribe(
      TopicArn=sns_topic_arn,
      Protocol='sqs',
      Endpoint=sqs_queue_arn
    )
    sns_subscription_arn = sns_subscribe["SubscriptionArn"]
    info_data = {
      "sqs_queue_url" : sqs_queue_url,
      "sns_subscription_arn" : sns_subscription_arn
    }
    info_data_json_object = json.dumps(info_data, indent = 4) 
  
    # Writing to info.json 
    with open(scripts_path+"/info.json", "w") as outfile: 
        outfile.write(info_data_json_object) 

    while True:
      syslog.syslog("LifeCycle Hook check for instance : " + host_instance_id + " :: Running")
      msg_json = sqs_client.receive_message(
        QueueUrl=sqs_queue_url,
        AttributeNames=[
            'All'
        ],
        MessageAttributeNames=[
            'All'
        ],
        MaxNumberOfMessages=10
      )
      try:
        if not msg_json["Messages"]:
          time.sleep(60)
          continue
      except Exception:
        time.sleep(60)
        continue

      num_msg = len(msg_json["Messages"])

      for index in range(num_msg):
        receipt_handle = msg_json["Messages"][index]["ReceiptHandle"]
        body = msg_json["Messages"][index]["Body"]
        body_msg_json = json.loads(body)["Message"]
        message = json.loads(body_msg_json)
        try:
          instance_id = message["EC2InstanceId"]
        except Exception:
          instance_id = "Not_Found"
          pass
        
        if instance_id in host_instance_id:
          AutoScalingGroupName = message["AutoScalingGroupName"]
          LifecycleActionToken = message["LifecycleActionToken"]
          LifecycleHookName = message["LifecycleHookName"]
          syslog.syslog("INFO:: Going Down, destroying...! ")
          destroy()
          try:
            # subscription unsubscribe
            sns_unsubscribe_response = sns_client.unsubscribe(
              SubscriptionArn=sns_subscription_arn
            )
            # queue delete
            sqs_delete_response = sqs_client.delete_queue(
              QueueUrl=sqs_queue_url
            )
            # call explicitly putback_hostnumber.py
            os.system('/opt/nuproj/putback_hostnumber.py')
            subprocess.check_output("/usr/sbin/logrotate --force /etc/logrotate.conf" , shell=True)
          except Exception:
            pass
          time.sleep(100)
          try:
            syslog.syslog("ASG Lifecycle signal continue!")
            asg_complete_lc_response = asg_client.complete_lifecycle_action(
              LifecycleHookName=LifecycleHookName,
              AutoScalingGroupName=AutoScalingGroupName,
              LifecycleActionToken=LifecycleActionToken,
              LifecycleActionResult='CONTINUE'
            )
          except Exception:
            pass
          return
        else:
          delete_msg_response = sqs_client.delete_message(
            QueueUrl=sqs_queue_url,
            ReceiptHandle=receipt_handle
          )
      time.sleep(40)
  except Exception, e:
    syslog.syslog("ERROR:: Some error occured in hooked lifecycle termination process.")

main()