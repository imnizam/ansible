#! /usr/bin/python

from ansible.module_utils.basic import *

def main():
  argument_spec = dict(
    environment=dict(required=True, type='str')
  )
  module = AnsibleModule(argument_spec=argument_spec)
  environment = module.params['environment']
  environment_short = environment[:3].lower()
  result = dict(changed=False, ansible_facts={
    'nuproj_environment': environment,
    'nuproj_environment_short': environment_short
  })
  module.exit_json(**result)

if __name__ == '__main__':
    main()
