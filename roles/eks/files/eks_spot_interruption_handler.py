import boto3
import paramiko
import os
def eks_spot_interruption_handler(event, context):
    try:
        ssh_user = os.environ['ssh_user']
    except:
        ssh_user = "ubuntu"
    #Get IP addresses of EC2 instances
    instance_id  = event['detail']['instance-id']
    region       = event['region']
    print "instance_id:" + str(instance_id)
    print "region:" + str(region)
    ec2_client   = boto3.client('ec2',region)
    ec2_response = ec2_client.describe_instances(InstanceIds=[instance_id])
    private_ip   = ec2_response['Reservations'][0]['Instances'][0]['PrivateIpAddress']
    s3_client    = boto3.client('s3',region)
    #Download private key file from secure S3 bucket
    s3_client.download_file('nuproj-ci-packages','ansible/lambda', '/tmp/keyname.pem')
    k = paramiko.RSAKey.from_private_key_file("/tmp/keyname.pem")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print "Connecting to " + private_ip
    c.connect( hostname = private_ip, username = ssh_user, pkey = k )
    print "Connected to " + private_ip

    commands = [
        "aws s3 --region " + region + " cp s3://nuproj-ecs-lambda/eks/scripts/spot_interruption_handler_for_lambda.sh /home/"+ssh_user+"/spot_interruption_handler_for_lambda.sh",
        "sudo chmod 777 /home/"+ssh_user+"/spot_interruption_handler_for_lambda.sh",
        "sudo /home/"+ssh_user+"/spot_interruption_handler_for_lambda.sh "+region
        ]
    for command in commands:
        print "Executing {}".format(command)
        stdin , stdout, stderr = c.exec_command(command)
        print stdout.read()
        print stderr.read()
