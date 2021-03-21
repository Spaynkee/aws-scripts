""" ch_create.py

    This class has several methods that wrap aws api calls, as well as some error handling.
    It inherits from the ch_base class.

"""

#pylint: disable=too-many-arguments

import os
import time
from botocore.exceptions import ClientError # type: ignore
from ch_base import CHBase

class CHCreate(CHBase):
    """ All methods of this class create aws resources or have otherwise constructive functions.

    """
    def __init__(self):
        CHBase.__init__(self)

    @classmethod
    def create_role(cls, name: str, json_file: str):
        """ This wraps the iam.create_role api call and creates a role with the specified name and
            json file containing the policy document

            Args:
                name: the name of the role to be created
                json_file: the filename of the policy document used to create the role.

        """
        print(f"creating role {name}")
        role_json = open(f"iam-roles/{json_file}", "r").read()

        try:
            response = cls.iam.create_role(RoleName=name,AssumeRolePolicyDocument=role_json)
        except ClientError as e:
            # I wonder if there's a better way for me to handle these errors?
            if e.response['Error']['Code'] == "EntityAlreadyExists":
                print("---Role already exists, skip for now.---")
            else:
                print(f"---Unhandled error: {e.response['Error']['Code']}---")

            return

        print(f"Created role {response['Role']['RoleName']}")

    @classmethod
    def create_policy(cls, policy_name: str, json_file: str):
        """ This wraps the iam.create_polcy api call and creates a custom policy
            with the specified  policy name and json file containing the policy document.

            Args:
                policy_name: the name of the policy to be created
                json_file: the filename of the policy document used to create the policy.

        """
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
    def attach_role_policy(cls, role_name: str, policy_arn: str):
        """ This wraps the iam.attach_role_policy api call and attaches a policy to a role.

            Args:
                role_name: the name of the role the policy is attached to.
                policy_arn: the arn of the policy being attached to the role.

        """
        print("attaching policy to role.")

        try:
            cls.iam.attach_role_policy(RoleName=role_name,PolicyArn=policy_arn)
        except ClientError as e:
            if e.response['Error']['Code'] == "":
                print("---Policy already attached? skip for now.---")
            else:
                print(f"---Unhandled error: {e.response['Error']['Code']}---")

            return

        print(f"Attached {policy_arn} to {role_name}")

    @classmethod
    def add_role_to_instance_profile(cls, instance_prof_name: str, role_name: str):
        """ This wraps the iam.add_role_to_instance_profile api call, which adds a role to an
            instance profile.

            Args:
                instance_prof_name: the name of the instance profile the role is added to.
                role_name: the name of the role being added to the instance profile.

        """
        print(f"attaching {role_name} to {instance_prof_name}")

        try:
            cls.iam.add_role_to_instance_profile(InstanceProfileName=instance_prof_name,\
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
        """ This wraps the iam.create_instance_profile api call, which creates an instance profile.

            Args:
                name: the name of the instance profile the role is added to.

        """
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
    def create_instance(cls, key_pair_name: str, prof_name: str, name: str, sg_name: str,\
            user_data_file: str =""):
        """ This wraps the ec2.resource.create_instances api call, which creates an instance.
            If one of the passed resources hasn't been fully created yet, this function waits
            5 seconds and tries again until it gets created.

            Args:
                key_pair_name: the name of the key pair used to create the instance.
                prof_name: the name of the instance profile used to create the instance.
                name: the name of the instance being created.
                sg_name: the name of the security group used to create the instance.
                user_data_file: filename of optional user data script used to create the instance.

        """
        print("Creating Instance")
        if user_data_file:
            user_data =  open("user-data/" + user_data_file, "r").read()

        try:
            cls.ec2res.create_instances(ImageId=cls.ami, MinCount=1, MaxCount=1,\
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
                print(f"---A resource wasn't created in time? Error:\n{e.response['Error']}---")
                print("\nWe'll wait a bit and try again")
                # we should wait a couple seconds and try again.
                time.sleep(5)
                cls.create_instance(key_pair_name, prof_name, name, sg_name, user_data_file)
            else:
                print(f"Unhandled error: {e.response['Error']['Code']}")
            return
        print("Created instance")

    @classmethod
    def create_instance_key_pair(cls, name: str):
        """ This wraps the ec2.client.create_key_pair api call, which creates a key pair.

            This function also creates a new .pem file and places it into my .ssh directory
            so that it can be used to ssh into the instance later if needed.

            Args:
                name: the name of the key pair used to create the instance.

        """
        print("Creating key pair for instance.")
        try:
            keypair = cls.ec2client.create_key_pair(KeyName=name)

            file_path = f"/Users/paul/.ssh/{name}.pem"
            # This only works for my file path, currently.
            private_key_file = open(file_path,"w")

            private_key_file.write(keypair['KeyMaterial'])
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
    def create_security_group(cls, name: str, desc: str):
        """ This wraps the ec2.client.create_security_group api call, which creates a security group

            Args:
                name: the name of the security group to be created.
                desc: the description of the security group.

        """
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
    def allow_port_security_group(cls, group_name: str, port: int):
        """ This wraps the ec2.client.authorize_security_group_ingress api call.
            ingress allows traffic in to the instance.

            Args:
                group_name: the name of the security group to be modified.
                port: the port number to be allowed.

        """
        print(f"allowing port {port} for security group {group_name}")
        group_id = cls.get_security_group_by_name(group_name)

        try:
            cls.ec2client.authorize_security_group_ingress(GroupId=group_id,\
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
    def create_rds_instance(cls, db_instance_id: str, sg_name: str):
        """ This wraps the rds.client.create_db_instance api call.

            Args:
                db_instance_id: the id of the db instance that will be created.
                sg_name: the name of the security group used with the db instance.

        """
        print(f"creating rds instance {db_instance_id}")

        db_sg = cls.get_security_group_by_name(sg_name)

        try:
            cls.rds.create_db_instance(DBInstanceIdentifier=db_instance_id,\
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

        print("Created db instance.")

    @classmethod
    def create_config(cls, file_name):
        """ Modifies the placeholder configs with the new rds endpoint, and uploads them to s3
            so they can be pulled down when the instance is created.

            More specifically this function replaces 'placeholder' with the rds endpoint in
            passed config files.

            Args:
                file_name: the name of config file to be edited.

        """
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
