#! /usr/bin/python

from ansible.module_utils.basic import *

def main():
  argument_spec = dict(
    region=dict(required=True, type='str')
  )
  module = AnsibleModule(argument_spec=argument_spec)

  region_names = {
    'us-east-2': 'Ohio',
    'us-east-1': 'N. Virginia',
    'us-west-1': 'N. California',
    'us-west-2': 'Oregon',
    'ap-south-1': 'Mumbai',
    'ap-northeast-2': 'Seoul',
    'ap-southeast-1': 'Singapore',
    'ap-southeast-2': 'Sydney',
    'ap-northeast-1': 'Tokyo',
    'ca-central-1': 'Central',
    'eu-central-1': 'Frankfurt',
    'eu-west-1': 'Ireland',
    'eu-west-2': 'London',
    'sa-east-1': 'Sao Paulo',
    'cn-north-1': 'beijing'
  }
  region_name_shorts = {
    'us-east-2': 'oh',
    'us-east-1': 'nv',
    'us-west-1': 'nc',
    'us-west-2': 'or',
    'ap-south-1': 'mb',
    'ap-northeast-2': 'sl',
    'ap-southeast-1': 'sg',
    'ap-southeast-2': 'sd',
    'ap-northeast-1': 'tk',
    'ca-central-1': 'ct',
    'eu-central-1': 'ff',
    'eu-west-1': 'ir',
    'eu-west-2': 'ld',
    'sa-east-1': 'sp',
    'cn-north-1': 'bj'
  }

  region = module.params['region']
  region_name = region_names[region]
  region_name_short = region_name_shorts[region]

  result = dict(changed=False, ansible_facts={
    'nuproj_region_name': region_name,
    'nuproj_region_name_short': region_name_short,
    'region': region
  })
  module.exit_json(**result)

if __name__ == '__main__':
    main()
