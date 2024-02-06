#! /usr/bin/python
import boto3
import requests
import syslog
from ansible.module_utils.basic import *

def main():
  argument_spec = dict(    
    instance_tags=dict(required=True, type='dict')
  )
  module = AnsibleModule(argument_spec=argument_spec)
  instance_tags = module.params['instance_tags']
  instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text
  az = requests.get('http://169.254.169.254/latest/meta-data/placement/availability-zone').text
  region = az[:-1]
  ec2_client = boto3.client('ec2',region_name=region)
  ec2_response = ec2_client.describe_instances(InstanceIds=[instance_id])
  lifecycle = ec2_response['Reservations'][0]['Instances'][0].get('InstanceLifecycle')

  if lifecycle is not None:
    try:
      asg_name = instance_tags['aws:autoscaling:groupName']
      launch_mode = "asg_fleet"
    except Exception:
      launch_mode = "fleet"
  else:
    try:
      asg_name = instance_tags['aws:autoscaling:groupName']
      launch_mode = "asg"
    except Exception:
      launch_mode = "ec2"

  result = dict(changed=False, ansible_facts={
    'LaunchMode': launch_mode
  })
  module.exit_json(**result)

if __name__ == '__main__':
    main()
