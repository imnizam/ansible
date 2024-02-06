#! /usr/bin/python
import boto3
import json
import os
import re
from ansible.module_utils.basic import *

def main():
  argument_spec = dict(
    es_role=dict(required=True, type='str'),
    consul_data=dict(required=True, type='dict')
  )
  module = AnsibleModule(argument_spec=argument_spec)
  es_role = module.params['es_role']
  consul_data = module.params['consul_data']

  es_configs = {}
  if "configs" in consul_data:
    es_configs = consul_data['configs']

  if es_role in ["master", "node"]:
    if "master" in consul_data:
      es_configs = dict(es_configs.items() + consul_data['master'].items())

  if es_role in ["data", "node"]:
    if "data" in consul_data:
      es_configs = dict(es_configs.items() + consul_data['data'].items())

  if es_role in ["ingest", "node"]:
    if "ingest" in consul_data:
      es_configs = dict(es_configs.items() + consul_data['ingest'].items())

  result = dict(changed=False, ansible_facts={
    'es_configs': es_configs,
  })
  module.exit_json(**result)

if __name__ == '__main__':
    main()
