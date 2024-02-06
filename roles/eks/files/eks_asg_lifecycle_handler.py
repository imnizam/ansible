import boto3
import paramiko
import os
def eks_asg_lifecycle_handler(event, context):
    print event
    try:
        ssh_user = os.environ['ssh_user']
    except:
        ssh_user = "ubuntu"
    #Get IP addresses of EC2 instances

    instance_id             =   event['detail']['EC2InstanceId']
    auto_scaling_group_name =   event['detail']['AutoScalingGroupName']
    lifecycle_action_token  =   event['detail']['LifecycleActionToken']
    lifecycle_hook_name     =   event['detail']['LifecycleHookName']
    region                  =   event['region']
    ec2_client = boto3.client('ec2',region)
    print "ssh_user: " + str(ssh_user)
    print "instance_id:" + str(instance_id)
    print "auto_scaling_group_name:" + str(auto_scaling_group_name)
    print "lifecycle_action_token:" + str(lifecycle_action_token)
    print "region:" + str(region)

    ec2_response = ec2_client.describe_instances(InstanceIds=[instance_id])
    private_ip = ec2_response['Reservations'][0]['Instances'][0]['PrivateIpAddress']
    print private_ip
    s3_client = boto3.client('s3',region)
    #Download private key file from secure S3 bucket
    s3_client.download_file('nuproj-ci-packages','ansible/lambda', '/tmp/keyname.pem')

    k = paramiko.RSAKey.from_private_key_file("/tmp/keyname.pem")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print "Connecting to " + str(private_ip)
    c.connect( hostname = private_ip, username = ssh_user, pkey = k )
    print "Connected to " + str(private_ip)

    commands = [
        "aws s3 --region " + region + " cp s3://nuproj-ecs-lambda/eks/scripts/asg_lifecycle_handler_for_lambda.sh /home/"+ssh_user+"/asg_lifecycle_handler_for_lambda.sh",
        "sudo chmod 777 /home/"+ssh_user+"/asg_lifecycle_handler_for_lambda.sh",
        "sudo /home/"+ssh_user+"/asg_lifecycle_handler_for_lambda.sh "+auto_scaling_group_name+" "+lifecycle_action_token+" "+lifecycle_hook_name+" "+region
        ]
    for command in commands:
        print "Executing {}".format(command)
        stdin , stdout, stderr = c.exec_command(command)
        print stdout.read()
        print stderr.read()
