# Base class that has all properties and info shared with the other class.
import boto3
import time

class CHBase():
    ami = "ami-09246ddb00c7c4fef" # linux-2 64bit Might parameterize this later idk
    iam = boto3.client('iam')
    ec2res = boto3.resource("ec2")
    ec2client = boto3.client("ec2")

    def __init__(self):
        return

    @classmethod
    def get_instance_id(cls, name, status):
        #returns an instance id based on passed name
        instances = cls.get_instances(status)

        # wait up to 30 seconds for an instance id
        for i in range(0, 6):
            for instance in instances:
                for tag in instance.tags:
                    if tag['Key'] == "Name" and tag['Value'] == name:
                        return instance.id
            print(f"Can't get instance ID. Maybe it's not {status} yet?")
            time.sleep(5)

        return ""


    @classmethod
    def get_instances(cls, status):
        #returns a list of instances based on status
        instances = cls.ec2res.instances.filter(
                    Filters=[{'Name': 'instance-state-name', 'Values': [status]}])

        return instances
