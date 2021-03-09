from CHBase import CHBase
from botocore.exceptions import ClientError
import time

# need to wrap all the actual API calls in a try-catch, with appropriate catches to retry if the resource already exists, or if the resource doesn't yet exist.
class CHCreate(CHBase):
    def __init__(self):
        CHBase.__init__(self)

    @classmethod
    def create_role(cls, name):
        print("creating role")
        role_json = open("iam-policy/instance-role.json", "r").read()

        try:
            response = cls.iam.create_role(RoleName=name,AssumeRolePolicyDocument=role_json)
        except ClientError as e:
            if e.response['Error']['Code'] == "EntityAlreadyExists":
                print("---Role already exists, skip for now.---")
            else:
                print(f"---Unhandled error: {e.response['Error']['Code']}---")

            return

        print(f"Created role {response['Role']['RoleName']}")

    @classmethod
    def create_instance_profile(cls, name):
        print("creating instance profile")
        try:
            response = cls.iam.create_instance_profile(InstanceProfileName=name)
        except ClientError as e:
            if e.response['Error']['Code'] == "EntityAlreadyExists":
                print("---Instance Profile already exists, skip for now.---")
            else:
                print(f"---Unhandled error: {e.response['Error']['Code']}---")
            return

        print(f"Created profile {response['InstanceProfile']['InstanceProfileName']}")


    @classmethod
    def create_instance(cls, key_pair_name, prof_name, name):
        print("Creating Instance")
        try:
            instances = cls.ec2res.create_instances(ImageId=cls.ami, MinCount=1, MaxCount=1,\
                    InstanceType="t2.micro",\
                    KeyName=key_pair_name,\
                    IamInstanceProfile={"Name": prof_name},\
                    TagSpecifications=[{\
                                    "ResourceType": "instance",
                                    "Tags":[{\
                                            "Key": "Name",\
                                            "Value": name}]\
                                    }])

        except ClientError as e:
            if e.response['Error']['Code'] == "":
                print("---Instance Profile already exists, skip for now.---")
            elif e.response['Error']['Code'] == "InvalidParameterValue":
                print(f"---Instance Profile wasn't created? Full error: \n{e.response['Error']}---")
                print("\nWe'll wait a bit and try again")
                # we should wait a couple seconds and try again.
                time.sleep(5)
                cls.create_instance(key_pair_name, prof_name, name)
            else:
                print(f"Unhandled error: {e.response['Error']['Code']}")
            return
        print("Created instance")

    @classmethod
    def create_instance_key_pair(cls, name):
        print("Creating key pair for instance.")
        try:
            cls.ec2client.create_key_pair(KeyName=name)
        except ClientError as e:
            # Populate here with the correct errors. Can't make because of missing key/prof/whatever
            if e.response['Error']['Code'] == "EntityAlreadyExists":
                print("---Instance key pair already exists, skip for now.---")
            else:
                print(f"---Unhandled error: {e.response['Error']['Code']}---")
            return
        print("Created key pair.")
