#! /usr/bin/python
import boto3
import os
from ansible.module_utils.basic import *

def main():
  argument_spec = dict(
    ec2_facts=dict(required=True, type='dict')
  )
  module = AnsibleModule(argument_spec=argument_spec)

  ec2_facts = module.params['ec2_facts']
  instance_id = ec2_facts['instance_id']
  private_ip = ec2_facts['private_ip_address']
  az = ec2_facts['placement']['availability_zone']
  region = az[:-1]
  cluster = ec2_facts['tags']['Cluster']
  service = ec2_facts['tags']['Service']
  hostname = os.uname()[1]

  ec2_client = boto3.client('ec2',region_name=region)
  reservations = ec2_client.describe_instances(Filters=[{'Name' : 'instance-state-name', 'Values' : ['running']},{'Name' : 'tag:Service', 'Values' : [service]},{'Name' : 'tag:Cluster', 'Values' : [cluster]}])

  host_list = []
  # for reservation in reservations["Reservations"] :
  #   for instance in reservation["Instances"]:
  #     host_list.append(instance['PrivateIpAddress'])

  for reservation in reservations["Reservations"] :
    for instance in reservation["Instances"]:
      for t in instance['Tags']:
        if t['Key'] == 'Name':
          host_list.append(t['Value'])

  host_list.sort()
  result = dict(changed=False, ansible_facts={
    'all_reservations': reservations,
    'zk_hostname': hostname,
    'all_zk_hosts': host_list
  })
  module.exit_json(**result)

if __name__ == '__main__':
    main()
