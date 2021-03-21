""" ch_base.py

    Contains the base class for both ch_create and ch_destroy to inherit from, and contains
    properties and functions used by both classes.

"""
import time
import configparser
import boto3 # type: ignore

class CHBase():
    """ The base class is inherited by both CHCreate and CHDestroy.

        Attributes:
            ami         (str): the arn of the ami used to create our web server
            iam         (obj): the iam client object provided by boto3
            ec2res      (obj): the ec2 resource object provided by boto3
            ec2client   (obj): the ec2 client object provided by boto3
            rds         (obj): the rds client object provided by boto3
            s3          (obj): the s3 client object provided by boto3
            vpc_id      (str): the id of the default vpc associated with out account
            db_config   (obj): ConfigParser object for reading config file
            db_user     (str): database user from config file
            db_password (str): database user password from config file
            bucket_name (str): the name of the bucket we're using for config files

    """
    ami = "ami-09246ddb00c7c4fef" # linux-2 64bit
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

    def __init__(self):
        return

    @classmethod
    def get_instance_id(cls, name: str, status: str) -> str:
        """ Returns the id of an instance based on its name and a passed status
            the status parameter filters instances by their status, so we can easily grab
            instance ids of 'running' instances, for example.

            Args:
                name: the name of the instance to get the id of.
                status: the status of the instance we want to get the id of.

            Returns:
                The instance id as a string if found within 30 seconds, or "" otherwise.

        """
        instances = cls.get_instances(status)

        # wait up to 30 seconds for an instance id
        for _ in range(0, 6):
            for instance in instances:
                for tag in instance.tags:
                    if tag['Key'] == "Name" and tag['Value'] == name:
                        return instance.id
            print(f"Can't get instance ID. Maybe it's not {status} yet?")
            time.sleep(5)
            instances = cls.get_instances(status)

        return ""


    @classmethod
    def get_instances(cls, status: str) -> list:
        """ Returns a list of instances based on their 'state name' (running, pending, etc)
            Wraps the ec2.resources.instances.filter api call.

            Args:
                status: the status of the instance we want to get the id of.

            Returns:
                A list of instances.

        """
        #returns a list of instances based on status
        instances = cls.ec2res.instances.filter(
                    Filters=[{'Name': 'instance-state-name', 'Values': [status]}])

        return instances

    @classmethod
    def get_security_group_by_name(cls, name: str) -> str:
        """ Returns a security group id based on the security groups name. Wraps the
            ec2.client.describe_security_groups api call.

            Args:
                name: The name of the security group we're getting the ID of.

            Returns:
                The security groups id as a string, or "" if the id was not found.

        """
        security_group_id = ""

        # wait up to 30 seconds for a security_group_id
        for _ in range(0, 6):

            response = cls.ec2client.describe_security_groups(Filters=[{'Name': 'group-name',\
                    'Values': [name]}])

            if response['SecurityGroups']:
                security_group_id = response['SecurityGroups'][0]['GroupId']
                return security_group_id

            print("Can't get security group id. Maybe it's not created yet?")
            time.sleep(5)
            cls.get_security_group_by_name(name)


        print("couldn't find sg_id after 30 seconds. Check yourself.")
        return security_group_id

    @classmethod
    def get_rds_endpoint(cls, db_identifier: str) -> str:
        """ Returns the endpoint of an rds instance based on the db_identifier we created it with.
            This function will wait indefinitely if there exists an rds instance that does not have
            an endpoint. Wraps the rds.client.describe_db_instances api call.

            Args:
                db_identifer: The identifier of the rds instance we're getting the endpoint for.

            Returns:
                The endpoint of the rds instance we specified in db_identifier as a string, or ""
                if there are no DB instances active.

        """
        res = cls.rds.describe_db_instances(DBInstanceIdentifier=db_identifier)

        if len(res['DBInstances']) > 0:
            while "Endpoint" not in res['DBInstances'][0]:
                time.sleep(10)
                res = cls.rds.describe_db_instances(DBInstanceIdentifier=db_identifier)
        else:
            return ""

        return res['DBInstances'][0]['Endpoint']['Address']

    @classmethod
    def upload_file_to_bucket(cls, file_name: str):
        """ uploads a specified file to the bucket associated with out base class.
            file will be uploaded to the bucket with the same filename as it has here.
            Wraps the s3.client.upload_file api call.

            Args:
                file_name: the name of the file to be uplaoded.

        """
        cls.s3.upload_file(file_name, cls.bucket_name, file_name)
