# Introduction

Sets basic facts including:

  * ansible_facts
  * ec2_metadata_facts
  * nuproj_instance_facts
  * nuproj_region_name, nuproj_region_name_short
  * nuproj_environment, nuproj_environment_short
  * nuproj_service
  * nuproj_cluster
  * nuproj_role
  * nuproj_hostname

# Required EC2 Instance Tags
* Environment: environment of the instance.

      e.g. production, staging.

* Service: service of the instance.

      e.g. elasticsearch, redis_sentinel, ecs.

# Optional EC2 Instance Tags
* Name: name of the instance, will be used as hostname and DNS name.
