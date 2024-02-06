#! /usr/bin/python
import boto3
import requests
from ansible.module_utils.basic import *

def main():
  argument_spec = dict(
    ec2_data=dict(required=True, type='dict')
  )
  module = AnsibleModule(argument_spec=argument_spec)
  
  ec2_facts = module.params['ec2_data']
  instance_id = ec2_facts['instance_id']
  private_ip = ec2_facts['private_ip_address']
  az = ec2_facts['placement']['availability_zone']
  region = az[:-1]
  cluster = ec2_facts['tags']['Cluster']
  service = ec2_facts['tags']['Service']
  ec2_client = boto3.client('ec2',region_name=region)

  seed_reservations = ec2_client.describe_instances(Filters=[{'Name' : 'instance-state-name', 'Values' : ['running']},{'Name' : 'tag:Service', 'Values' : [service]},{'Name' : 'tag:Cluster', 'Values' : [cluster]},{'Name' : 'tag:seed', 'Values' : ['true']}])
  seed_host_list = []

  for seed_reservation in seed_reservations["Reservations"] :
    for seed_instance in seed_reservation["Instances"]:
      seed_host_list.append(seed_instance["PrivateIpAddress"])

  if len(seed_host_list) == 0:
    seed_host_list.append(private_ip)

  # search for seed=true and AZ=az
  reservations = ec2_client.describe_instances(Filters=[{'Name' : 'instance-state-name', 'Values' : ['running']},{'Name' : 'tag:Service', 'Values' : [service]},{'Name' : 'tag:Cluster', 'Values' : [cluster]},{'Name' : 'tag:seed', 'Values' : ['true']},{'Name' : 'availability-zone', 'Values' : [az]}])
  host_list = []
  for reservation in reservations["Reservations"] :
    for instance in reservation["Instances"]:
      host_list.append(instance["PrivateIpAddress"])

  if len(host_list) == 0:
    ec2_client.create_tags( Resources=[instance_id], Tags=[{ 'Key': 'seed', 'Value': 'true' }] )

  result = dict(changed=False, ansible_facts={
    'seeds': ','.join(seed_host_list)
  })
  module.exit_json(**result)

if __name__ == '__main__':
    main()
