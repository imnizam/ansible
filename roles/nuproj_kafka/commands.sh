###########
# zookeeper
###########
# install zookeeper
ansible-playbook ./zookeeper.yml --extra-vars "zookeeper_tag=Service_zookeeper" --tags install

# start zookeepr
ansible-playbook ./zookeeper.yml --extra-vars "zookeeper_tag=Service_zookeeper" --tags start

# stop zookeeper
ansible-playbook ./zookeeper.yml --extra-vars "zookeeper_tag=Service_zookeeper" --tags stop

# info zookeeper
ansible-playbook ./zookeeper.yml --extra-vars "zookeeper_tag=Service_zookeeper" --tags info

#########
# Kafka
#########
# install kafka
ansible-playbook ./kafka.yml  --tags install
# start kafka
ansible-playbook ./kafka.yml --extra-vars "zookeeper_tag=Service_zookeeper kafka_tag=Service_kafka" --tags start
# stop kafka
ansible-playbook ./kafka.yml --extra-vars "zookeeper_tag=Service_zookeeper kafka_tag=Service_kafka" --tags stop
# info kafka
ansible-playbook ./kafka.yml --extra-vars "zookeeper_tag=Service_zookeeper kafka_tag=Service_kafka" --tags info













