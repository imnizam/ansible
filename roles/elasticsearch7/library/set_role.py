#! /usr/bin/python
import boto3
import json
import os
import re
from ansible.module_utils.basic import *

def main():
  argument_spec = dict(
    region=dict(required=True, type='str'),
    ec2_data=dict(required=True, type='dict'),
  )
  module = AnsibleModule(argument_spec=argument_spec)
  region = module.params['region']
  ec2_data = module.params['ec2_data']
  instance_id = ec2_data['instance_id']
  hostname = os.uname()[1]
  es_role = re.compile(r'\d+').sub('',hostname).split('-')[-1]

  ec2_client = boto3.client('ec2',region)
  ec2_client.create_tags( Resources=[ instance_id ], Tags=[{ 'Key': 'Role', 'Value': es_role }] )

  result = dict(changed=False, ansible_facts={
    'es_role': es_role
  })
  module.exit_json(**result)

if __name__ == '__main__':
    main()
