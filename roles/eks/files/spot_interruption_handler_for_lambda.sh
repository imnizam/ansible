#!/bin/bash

region=${1}

KUBECONFIG=/var/lib/kubelet/kubeconfig
NODENAME=$(curl -Gs http://localhost:10255/pods/ | grep -o '"nodeName":"[^"]*"' | awk -F[:] 'NR==1{print $2}' | tr -d '"')

#Mark node for drain
kubectl --kubeconfig ${KUBECONFIG} drain ${NODENAME} --grace-period=30 --ignore-daemonsets=true --force  &


#force log rotate
/usr/sbin/logrotate --force /etc/logrotate.conf &
