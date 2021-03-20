from CHBase import CHBase
from botocore.exceptions import ClientError
import os
import time

class CHCreate(CHBase):
    def __init__(self):
        CHBase.__init__(self)

    @classmethod
    def create_role(cls, name, json_file):
        print(f"creating role {name}")
        role_json = open(f"iam-roles/{json_file}", "r").read()

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
    def create_policy(cls, policy_name, json_file):
        print("creating policy")
        policy_json = open(f"iam-policies/{json_file}", "r").read()

        try:
            response = cls.iam.create_policy(PolicyName=policy_name,PolicyDocument=policy_json)
        except ClientError as e:
            if e.response['Error']['Code'] == "EntityAlreadyExists":
                print("---Policy already exists, skip for now.---")
            else:
                print(f"---Unhandled error: {e.response['Error']['Code']}---")

            return

        print(f"Created role {response['Policy']['PolicyName']}")


    @classmethod
    def attach_role_policy(cls, role_name, policy_arn):
        print("attaching policy to role.")

        try:
            response = cls.iam.attach_role_policy(RoleName=role_name,PolicyArn=policy_arn)
        except ClientError as e:
            if e.response['Error']['Code'] == "":
                print("---Policy already attached? skip for now.---")
            else:
                print(f"---Unhandled error: {e.response['Error']['Code']}---")

            return

        print(f"Attached {policy_arn} to {role_name}")

    @classmethod
    def add_role_to_instance_profile(cls, instance_prof_name, role_name):
        print(f"attaching {role_name} to {instance_prof_name}")

        try:
            response = cls.iam.add_role_to_instance_profile(InstanceProfileName=instance_prof_name,\
                    RoleName=role_name)
        except ClientError as e:
            if e.response['Error']['Code'] == "":
                print("---Policy already attached? skip for now.---")
            else:
                print(f"---Unhandled error: {e.response['Error']['Code']}---")

            return

        print(f"Attached {role_name} to {instance_prof_name}")

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
    def create_instance(cls, key_pair_name, prof_name, name, sg_name, user_data_file=""):
        print("Creating Instance")
        if user_data_file:
            user_data =  open("user-data/" + user_data_file, "r").read()

        try:
            instances = cls.ec2res.create_instances(ImageId=cls.ami, MinCount=1, MaxCount=1,\
                    InstanceType="t2.micro",\
                    KeyName=key_pair_name,\
                    IamInstanceProfile={"Name": prof_name},\
                    UserData=user_data,
                    SecurityGroups=[sg_name],
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
                print(f"---A resource wasn't created in time? Full error: \n{e.response['Error']}---")
                print("\nWe'll wait a bit and try again")
                # we should wait a couple seconds and try again.
                time.sleep(5)
                cls.create_instance(key_pair_name, prof_name, name, sg_name, user_data_file)
            else:
                print(f"Unhandled error: {e.response['Error']['Code']}")
            return
        print("Created instance")

    @classmethod
    def create_instance_key_pair(cls, name):
        print("Creating key pair for instance.")
        try:
            keypair = cls.ec2client.create_key_pair(KeyName=name)

            file_path = f"/Users/paul/.ssh/{name}.pem"
            # This only works for my file path, currently.
            private_key_file = open(file_path,"w")
            # might want to chmod 400 here too, if we can?

            private_key_file.write(keypair['KeyMaterial'])
            private_key_file.close
            os.chmod(file_path, 0o400)

        except ClientError as e:
            # Populate here with the correct errors. Can't make because of missing key/prof/whatever
            if e.response['Error']['Code'] == "InvalidKeyPair.Duplicate":
                print("---Instance key pair already exists, skip for now.---")
            else:
                print(f"---Unhandled error: {e.response['Error']['Code']}---")
            return
        print("Created key pair and .pem file.")

    @classmethod
    def create_security_group(cls, name, desc):
        print("creating security group")

        try:
            response = cls.ec2client.create_security_group(GroupName=name, Description=desc,\
                    VpcId=cls.vpc_id)
        except ClientError as e:
            if e.response['Error']['Code'] == "InvalidGroup.Duplicate":
                print("---Security group already exists, skip for now.---")
            else:
                print(f"---Unhandled error: {e.response['Error']['Code']}---")

            return

        print(f"Created security group {response['GroupId']}")

    @classmethod
    def allow_port_security_group(cls, group_name, port):
        print(f"allowing port {port} for security group {group_name}")
        group_id = cls.get_security_group_by_name(group_name)

        try:
            response = cls.ec2client.authorize_security_group_ingress(GroupId=group_id,\
                    IpPermissions=[{'IpProtocol': "tcp",\
                    'FromPort': port, \
                    'ToPort': port, \
                    'IpRanges':[{'CidrIp': '0.0.0.0/0'}]}])

        except ClientError as e:
            # What errors do we capture?
            if e.response['Error']['Code'] == "InvalidPermission.Duplicate":
                print("---Your port permission already exists. Skip for now.---")
            else:
                print(f"---Unhandled error: {e.response['Error']['Code']}---")

            return

        print(f"Allowed {port} for SG {group_id}")

    @classmethod
    def create_rds_instance(cls, db_instance_id, sg_name):
        print(f"creating rds instance {db_instance_id}")

        db_sg = cls.get_security_group_by_name(sg_name)

        try:
            response = cls.rds.create_db_instance(DBInstanceIdentifier=db_instance_id,\
                    AllocatedStorage=20,\
                    DBName="Lstats",\
                    Engine="mysql",
                    StorageType="gp2",
                    MasterUsername=cls.db_user,\
                    MasterUserPassword=cls.db_password,\
                    VpcSecurityGroupIds=[db_sg],\
                    DBInstanceClass="db.t2.micro")

        except ClientError as e:
            if e.response['Error']['Code'] == "EntityAlreadyExists":
                print("---Instance already exists? Skip for now.---")
            elif e.response['Error']['Code'] == "InvalidParameterValue":
                print(f"---{e.response['Error']}---")
            elif e.response['Error']['Code'] == "InvalidParameterCombination":
                print(f"---{e.response['Error']}---")
            else:
                print(f"---Unhandled error: {e.response['Error']}---")

            return

        print(f"Created db instance.")

    @classmethod
    def create_config(cls, file_name):
        print(f"Updating the config file named {file_name}")

        # get the endpoint
        endpoint = cls.get_rds_endpoint('rds-is-cool')
        with open(f'{file_name}', 'r') as file :
            filedata = file.read()

            filedata = filedata.replace('placeholder', endpoint)

            with open(f'{file_name}', 'w') as file:
                file.write(filedata)

        # upload to s3
        cls.upload_file_to_bucket(file_name)
        print(f"Updated {file_name} and stored in bucket.")
