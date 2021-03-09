from CHBase import CHBase
from botocore.exceptions import ClientError

class CHDelete(CHBase):
    # I should have all properties on the base class here.
    def __init__(self):
        CHBase.__init__(self)

    @classmethod
    def destroy_role(cls, name):
        print("Deleting role")
        try:
            response = cls.iam.delete_role(RoleName=name)
        except ClientError as e:
            # Populate here with the correct errors. Can't make because of missing key/prof/whatever
            if e.response['Error']['Code'] == "NoSuchEntity":
                print("Instance role didn't exist, skip for now.")
            else:
                print(f"Unhandled error: {e.response['Error']['Code']}")
            return

        print(f"Destroyed role")

    @classmethod
    def destroy_instance_profile(cls, name):
        print("Deleting instance profile")
        try:
            response = cls.iam.delete_instance_profile(InstanceProfileName=name)
        except ClientError as e:
            # Populate here with the correct errors. Can't make because of missing key/prof/whatever
            if e.response['Error']['Code'] == "NoSuchEntity":
                print("Instance Profile didn't exist, skip for now.")
            else:
                print(f"Unhandled error: {e.response['Error']['Code']}")
            return
        print(f"Deleted profile")

    @classmethod
    def destroy_instance_key_pair(cls, name):
        print("Deleting key pair for instance.")
        try:
            cls.ec2client.delete_key_pair(KeyName=name)
        except ClientError as e:
            # Populate here with the correct errors. Can't make because of missing key/prof/whatever
            if e.response['Error']['Code'] == "NoSuchEntity":
                print("Instance key pair didn't exist, skip for now.")
            else:
                print(f"Unhandled error: {e.response['Error']['Code']}")
            return
        print("Deleted key pair.")
        return

    @classmethod
    def destroy_instance(cls, name):
        # We have to get a list of instances, and get the right id so we can terminate.
        
        instance_id = cls.get_instance_id(name, 'running')

        print(f"Terminating Instance '{instance_id}'")
            
        try:
            cls.ec2res.Instance(instance_id).terminate()
        except ClientError as e:
            # Populate here with the correct errors. Can't make because of missing key/prof/whatever
            if e.response['Error']['Code'] == "InvalidInstanceID.Malformed":
                print(f"Couldn't terminate instance '{instance_id}', skip for now?")
            else:
                print(f"Unhandled error: {e.response['Error']['Code']}")
            return
        return
        
        print("Terminated Instance")
        return


