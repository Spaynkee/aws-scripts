# Base class that has all properties and info shared with the other class.
import boto3
import time
import configparser

class CHBase():
    ami = "ami-09246ddb00c7c4fef" # linux-2 64bit Might parameterize this later
    iam = boto3.client('iam')
    ec2res = boto3.resource("ec2")
    ec2client = boto3.client("ec2")
    rds = boto3.client("rds")
    s3 = boto3.client("s3")
    vpc_id = "vpc-a37d3ccb" # our default vpc
    db_config = configparser.ConfigParser()
    db_config.read('general.cfg')
    db_user = db_config.get("DATABASE", "db_user")
    db_password = db_config.get("DATABASE", "db_password")
    bucket_name = "super-cool-bucket-1337-pb"
    # add bucket name?

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
            instances = cls.get_instances(status)

        return ""


    @classmethod
    def get_instances(cls, status):
        #returns a list of instances based on status
        instances = cls.ec2res.instances.filter(
                    Filters=[{'Name': 'instance-state-name', 'Values': [status]}])

        return instances

    @classmethod
    def get_security_group_by_name(cls, name):
        security_group_id = ""

        # wait up to 30 seconds for a security_group_id
        for i in range(0, 6):

            response = cls.ec2client.describe_security_groups(Filters=[{'Name': 'group-name',\
                    'Values': [name]}])

            if response['SecurityGroups']:
                security_group_id = response['SecurityGroups'][0]['GroupId']
                return security_group_id
            else:
                print(f"Can't get security group id. Maybe it's not created yet?")
                time.sleep(5)
                cls.get_security_group_by_name(name)


        print(f"couldn't find sg_id after 30 seconds. Check yourself.")
        return security_group_id

    @classmethod
    def get_rds_endpoint(cls, db_identifier):
        #returns info about our rds?
        res = cls.rds.describe_db_instances(DBInstanceIdentifier=db_identifier)
        return res['DBInstances'][0]['Endpoint']['Address']

    @classmethod
    def upload_file_to_bucket(cls, file_name):
        cls.s3.upload_file(file_name, cls.bucket_name, file_name)
