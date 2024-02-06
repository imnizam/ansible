#!/bin/bash

#Commands
# setup ssh with all node of a cluster , trigger with only one node
scyllamgr_ssh_setup --ssh-user ubuntu --ssh-identity-file /home/ubuntu/.ssh/key.pem <ip_any_node>

# add given cluster to scylla manager , give cluster name flag

sctool cluster add --host <ip_any_node> -n 'cluster_name' --ssh-user 'scylla-manager' --ssh-identity-file '/home/ubuntu/.ssh/scylla-manager.pem'

sctool cluster --help
Commands: add, delete , list

sctool task list/progress/update -c cluster


