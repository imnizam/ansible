#! /usr/bin/python
import boto3
import requests
import redis
from ansible.module_utils.basic import *

def main():
  argument_spec = dict(
    ec2_facts=dict(required=True, type='dict'),
    consul_data=dict(required=True, type='dict')
  )
  module = AnsibleModule(argument_spec=argument_spec)
  
  ec2_facts     = module.params['ec2_facts']
  consul_data   = module.params['consul_data']

  cluster       = consul_data['MonitoredCluster']
  service       = consul_data['MonitoredService']
  az            = ec2_facts['placement']['availability_zone']
  region        = az[:-1]

  ec2_client    = boto3.client('ec2',region_name=region)

  master_reservations = ec2_client.describe_instances(Filters=[{'Name' : 'instance-state-name', 'Values' : ['running']},{'Name' : 'tag:Service', 'Values' : [service]},{'Name' : 'tag:Cluster', 'Values' : [cluster]}])
  master_host_list = []

  for master_reservation in master_reservations["Reservations"] :
    for master_instance in master_reservation["Instances"]:
      master_host_list.append(master_instance["PrivateIpAddress"])

  master_host_ip = "127.0.0.1"

  for node in master_host_list:
    try:
      redis_client  = redis.Redis(host=node, port=9851)
      node_info     = redis_client.info()
      if node_info['role'] == 'master':
        master_host_ip = node
      else:
        master_host_ip = node_info['master_host']
      break
    except Exception, e:
      syslog.syslog("INFO:: node " + node + " is down!, trying query other node for master discovery.")

  result = dict(changed=False, ansible_facts={
    'master_ip': master_host_ip
  })
  module.exit_json(**result)

if __name__ == '__main__':
    main()
