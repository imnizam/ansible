#! /usr/bin/python
import boto3
import os
import subprocess
import requests
import json
import re
import base64
from ansible.module_utils.basic import *

def main():
  argument_spec = dict(
    internal_ip=dict(required=True, type='str'),
    region=dict(required=True, type='str'),
    instance_tags=dict(required=True, type='dict'),
    service=dict(required=True, type='str')
  )
  module = AnsibleModule(argument_spec=argument_spec)

  internal_ip = module.params['internal_ip']
  region = module.params['region']
  instance_tags = module.params['instance_tags']
  service = module.params['service']

  eks_cluster = instance_tags['Cluster']
  eks_client = boto3.client('eks','us-west-2')
  eks_cluster_response =  eks_client.describe_cluster(name=eks_cluster)
  eks_ca_cert_data =  eks_cluster_response["cluster"]["certificateAuthority"]["data"]
  eks_ca_cert_data_rsa = base64.b64decode(eks_ca_cert_data)
  eks_cluster_endpoint = eks_cluster_response["cluster"]["endpoint"]
  dns_cluster_ip_addr = "172.20.0.10"

  ca_certificate_directory = "/etc/kubernetes/pki"
  ca_certificate_file_path = ca_certificate_directory + "/ca.crt"
  # model_directory_path = os.getenv("HOME") + "/.aws/eks"
  model_directory_path = "/home/ubuntu/.aws/eks"
  model_file_path = model_directory_path + "/eks-2017-11-01.normal.json"

  subprocess.check_output("mkdir -m 0755 -p " + ca_certificate_directory, shell=True)
  subprocess.check_output("mkdir -m 0755 -p " + model_directory_path, shell=True)

  model_file = requests.get('https://s3-us-west-2.amazonaws.com/amazon-eks/1.10.3/2018-06-05/eks-2017-11-01.normal.json').json()
  with open(model_file_path, 'w') as mfile:
    json.dump(model_file, mfile)

  subprocess.check_output("aws --region " + region + " configure add-model --service-model file://"+ model_file_path + " --service-name eks" , shell=True)

  with open(ca_certificate_file_path, 'w') as cafile:
    cafile.write(eks_ca_cert_data_rsa)

  if re.match("10.*", internal_ip):
    dns_cluster_ip_addr = "172.20.0.10"
  else:
    dns_cluster_ip_addr = "10.100.0.10"


  result = dict(changed=False, ansible_facts={
    'cluster_name': instance_tags['Cluster'],
    'dns_cluster_ip': dns_cluster_ip_addr,
    'certificate_authority_file': ca_certificate_file_path,
    'master_endpoint': eks_cluster_endpoint
  })
  module.exit_json(**result)

if __name__ == '__main__':
    main()
