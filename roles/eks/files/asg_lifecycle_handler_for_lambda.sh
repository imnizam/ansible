#!/bin/bash

auto_scaling_group_name=${1}
lifecycle_action_token=${2}
lifecycle_hook_name=${3}
region=${4}

KUBECONFIG=/var/lib/kubelet/kubeconfig
NODENAME=$(curl -Gs http://localhost:10255/pods/ | grep -o '"nodeName":"[^"]*"' | awk -F[:] 'NR==1{print $2}' | tr -d '"')

#Mark node for drain
kubectl --kubeconfig ${KUBECONFIG} drain ${NODENAME} --grace-period=30 --ignore-daemonsets=true --force  &
#force log rotate
/usr/sbin/logrotate --force /etc/logrotate.conf &


# sleep 300
# aws autoscaling complete-lifecycle-action --region ${region}  \
#   --lifecycle-hook-name ${lifecycle_hook_name} \
#   --auto-scaling-group-name ${auto_scaling_group_name} \
#   --lifecycle-action-result CONTINUE \
#   --lifecycle-action-token ${lifecycle_action_token}