# Introduction

Configures and starts ecs service.

# Expected variables or facts

* **nuproj_script_home(inferred)**: central place for nuproj scripts, inferred in role `basic_setup`.

# Role Dependency

* **basic_setup**
* **basic_facts**


**NOTE := Must Read**

*AutoScalingGroup and spot fleet termination protection is being handled by lambda function.Whenever there is any ASG downscaling , lifecycle hook puts instance in terminate wait state and an event is triggered to cloudwatch even rule. This rule triggers lambda function that executes handler file after doing ssh. In same way, in spot fleet when an instance is marked for termination it triggers a cloudwatch event, that in turn handled by lambda function.*

**ASG:
    Two files:
      1)ecs_asg_lifecycle_handler.py
      2)asg_lifecycle_handler_for_lambda.sh
Spot Fleet:
    Two files:
      1)ecs_spot_interruption_handler.py
      2)spot_interruption_handler_for_lambda.sh**


**How to create lambda function deployment package:**
Using python virtualenv: *pip install virtualenv*
1. mkdir lambda-env;cd lambda-env
2. virtualenv –p /usr/bin/python2.7 .
3. source bin/activate
4. pip install pycrypto
5. pip install paramiko
6. copy <path>/ecs_asg_lifecycle_handler.py to lib/python2.7/site-packages
7. cd lib/python2.7/site-packages
8. zip -r9 <zip_path>/ecs_asg_lifecycle_handler.zip .
   Make sure you put . in the end and never use * as it skips hidden library files.
9. upload this zip to s3 ; aws s3 cp ecs_asg_lifecycle_handler.zip  s3://nuproj-ecs-lambda/eks/lambda/
10. upload handler shell script to s3 also; aws s3 cp asg_lifecycle_handler_for_lambda.sh  s3://nuproj-ecs-lambda/eks/scripts/
< *Likewise for spot fleet*>

*Here you have the flexibility to change handler behavior without changing lambda function code. Only change sheel script of handler and upload it to s3. Lambda function pulls it at runtime on the target instance.*

**Also: Dont change any filename or function name in lambda function code. as same naming is being used in terraform for lambda function creation.**

**EKS cluster node Authorization**
https://docs.aws.amazon.com/eks/latest/userguide/add-user-role.html
