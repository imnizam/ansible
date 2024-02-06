#!/bin/bash

# De-register from ECS cluster
data=`curl -s http://localhost:51678/v1/metadata | jq .`
cluster=`echo $data | jq -r '.Cluster'`
instance_arn=`echo $data | jq -r '.ContainerInstanceArn'`
aws ecs deregister-container-instance --region=us-west-2 --cluster $cluster --container-instance ${instance_arn} --force

# Service stop datadog agent
sudo systemctl stop datadog-agent.service
# Service stop ecs agent
sudo systemctl stop ecs_agent.service

instance_id=`curl -s http://169.254.169.254/latest/meta-data/instance-id`

# De-register this instance from all ALB target groups,
# that it has containers running

# List all containers Ids having tcp port open
alb_container_ids=$(docker ps -f status=running | awk '/tcp/{print $1}')

# De-register this instance from all target groups
for container_id in ${alb_container_ids[@]}
do
  container_info=$(docker inspect  $container_id)
  task_arn=$(echo $container_info | jq -r '.[].Config.Labels | .["com.amazonaws.ecs.task-arn"]')
  cluster=$(echo $container_info  | jq -r '.[].Config.Labels | .["com.amazonaws.ecs.cluster"]')
  service_name=$(aws ecs --region us-west-2  describe-tasks --tasks $task_arn --cluster $cluster | jq -r '.tasks[].group' | awk -F[:] '{print $2}')
  service_info=$(aws ecs --region us-west-2  describe-services --services $service_name --cluster $cluster)
  targetgroup_arn=$(echo $service_info| jq -r '.services[].loadBalancers[].targetGroupArn')
  serving_port=$(echo $service_info| jq -r '.services[].loadBalancers[].containerPort')
  serving_proto="\"${serving_port}/tcp\""
  host_mapped_port=$(echo $container_info | jq -r ".[].NetworkSettings.Ports | .[$serving_proto] | .[0].HostPort")
  # "Removing $instance_id from $targetgroup_arn at $host_mapped_port"
  aws elbv2 --region us-west-2 deregister-targets --target-group-arn ${targetgroup_arn} --targets Id="${instance_id}",Port="${host_mapped_port}" &
done

# Kill worker docker containers ,ie, those not attached to ALB
worker_container_ids=$(docker ps -f status=running | awk 'NR>1 && !/tcp/{print $1}')
docker stop -t 45 ${worker_container_ids} &
/usr/sbin/logrotate --force /etc/logrotate.conf &

sleep 10
# Kill ALB attached docker containers
docker stop -t 15 ${alb_container_ids} &
