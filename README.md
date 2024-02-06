# ansible

Packer is used to build EC2 AMI. All ansible tasks are labelled with "live" and other tags. At AMI build time "live" tags are skipped. At boot time playbook is executed again only for "live" tags. 

For dynamic configuration and environment specific customization , consul key/value is used. Refer "roles/basic_facts" for consul tags.