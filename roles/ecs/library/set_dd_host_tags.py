#! /usr/bin/python
import boto3
from ansible.module_utils.basic import *

def main():
  argument_spec = dict(
    instance_id=dict(required=True, type='str'),
    region=dict(required=True, type='str'),
    filter_tags_prefix=dict(required=False, type='list')
  )
  module = AnsibleModule(argument_spec=argument_spec)

  instance_id = module.params['instance_id']
  region = module.params['region']
  filter_tags_prefix = module.params['filter_tags_prefix']

  ec2_client = boto3.client('ec2',region_name=region)
  ec2_response = ec2_client.describe_instances(InstanceIds=[instance_id])
  tags = ec2_response['Reservations'][0]['Instances'][0]['Tags']

  host_tags_list = []
  for tag in tags:
    host_tags_list.append(tag['Key']+':'+tag['Value'])

  datadog_host_tags = host_tags_list[:]
  for prefix in filter_tags_prefix:
    for tag in tags:
        if prefix in tag['Key']:
          try:
            datadog_host_tags.remove(tag['Key']+':'+tag['Value'])
          except ValueError:
            pass

  result = dict(changed=False, ansible_facts={
    'datadog_host_tags': ', '.join(datadog_host_tags)
  })
  module.exit_json(**result)

if __name__ == '__main__':
    main()
