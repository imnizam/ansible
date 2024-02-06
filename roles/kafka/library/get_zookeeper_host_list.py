#! /usr/bin/python
import boto3
from ansible.module_utils.basic import *

def main():
  argument_spec = dict(
    region=dict(required=True, type='str'),
    consul_data=dict(required=True, type='dict')
  )
  module = AnsibleModule(argument_spec=argument_spec)

  region = module.params['region']
  consul_data = module.params['consul_data']
  
  zookeeper_cluster = consul_data['ZooKeeperCluster']
  ec2_client = boto3.client('ec2',region_name=region)
  reservations = ec2_client.describe_instances(Filters=[{'Name' : 'instance-state-name', 'Values' : ['running']},{'Name' : 'tag:Service', 'Values' : ['zookeeper']},{'Name' : 'tag:Cluster', 'Values' : [zookeeper_cluster]}])

  host_list = []

  for reservation in reservations["Reservations"] :
    for instance in reservation["Instances"]:
      for t in instance['Tags']:
        if t['Key'] == 'Name':
          host_list.append(t['Value'])

  host_list.sort()
  result = dict(changed=False, ansible_facts={
    'zookeeper_hosts': host_list
  })
  module.exit_json(**result)

if __name__ == '__main__':
    main()
