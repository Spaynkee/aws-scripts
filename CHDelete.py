from CHBase import CHBase
from botocore.exceptions import ClientError
import time
import os

class CHDelete(CHBase):
    def __init__(self):
        CHBase.__init__(self)

    @classmethod
    def destroy_role(cls, name):
        print("Deleting role")
        try:
            response = cls.iam.delete_role(RoleName=name)
        except ClientError as e:
            if e.response['Error']['Code'] == "NoSuchEntity":
                print("Instance role didn't exist, skip for now.")
            elif e.response['Error']['Code'] == "DeleteConflict":
                print("Role still has policies attached. Remove those and try again.")
            else:
                print(f"Unhandled error: {e.response['Error']['Code']}")
            return

        print(f"Destroyed role")

    @classmethod
    def detach_role_policy(cls, role_name, policy_arn):
        print("removing policy from role.")

        try:
            response = cls.iam.detach_role_policy(RoleName=role_name,PolicyArn=policy_arn)
        except ClientError as e:
            if e.response['Error']['Code'] == "NoSuchEntity":
                print("---Policy already removed? skip for now.---")
            else:
                print(f"---Unhandled error: {e.response['Error']['Code']}---")

            return

        print(f"Removed {policy_arn} from {role_name}")

    @classmethod
    def remove_role_from_instance_profile(cls, instance_prof_name, role_name):
        print(f"removing {role_name} from {instance_prof_name}")

        try:
            res = cls.iam.remove_role_from_instance_profile(InstanceProfileName=instance_prof_name,\
                    RoleName=role_name)
        except ClientError as e:
            if e.response['Error']['Code'] == "NoSuchEntity":
                print("---Role not attached to profile? skip for now.---")
            else:
                print(f"---Unhandled error: {e.response['Error']['Code']}---")

            return

        print(f"Removed {role_name} from {instance_prof_name}")

    @classmethod
    def destroy_policy(cls, policy_arn):
        print(f"Deleting policy {policy_arn}")
        try:
            response = cls.iam.delete_policy(PolicyArn=policy_arn)
        except ClientError as e:
            if e.response['Error']['Code'] == "NoSuchEntity":
                print("Policy didn't exist, skip for now.")
            else:
                print(f"Unhandled error: {e.response['Error']['Code']}")
            return

        print(f"Destroyed policy")

    @classmethod
    def destroy_instance_profile(cls, name):
        print("Deleting instance profile")
        try:
            response = cls.iam.delete_instance_profile(InstanceProfileName=name)
        except ClientError as e:
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
            os.remove(f"/Users/paul/.ssh/{name}.pem")
        except ClientError as e:
            if e.response['Error']['Code'] == "NoSuchEntity":
                print("Instance key pair didn't exist, skip for now.")
            else:
                print(f"Unhandled error: {e.response['Error']['Code']}")
            return
        except FileNotFoundError as e:
            print("File didn't exist, so we couldn't delete it")

        print("Deleted key pair and .pem file.")
        return

    @classmethod
    def destroy_instance(cls, name):
        # We have to get a list of instances, and get the right id so we can terminate.
        # might want to see if any instances exist at all, and if not then just skip this.
        instance_id = cls.get_instance_id(name, 'running')

        print(f"Terminating Instance '{instance_id}'")
            
        try:
            cls.ec2res.Instance(instance_id).terminate()
        except ClientError as e:
            if e.response['Error']['Code'] == "InvalidInstanceID.Malformed":
                print(f"Couldn't terminate instance '{instance_id}', skip for now?")
            else:
                print(f"Unhandled error: {e.response['Error']['Code']}")
            return
        return
        
        print("Terminated Instance")
        return

    @classmethod
    def destroy_security_group(cls, name):
        # This fails if the instance is still running. Have to make sure the instance is terminated first.
        print(f"Deleting security group {name}")
        try:
            cls.ec2client.delete_security_group(GroupName=name)
        except ClientError as e:
            if e.response['Error']['Code'] == "InvalidGroup.NotFound":
                print(f"Security group {name} didn't exist, skip for now.")
            elif e.response['Error']['Code'] == "DependencyViolation":
                print(f"Security group in use by instance. Maybe it hasn't terminated yet?")
                print("\nWe'll wait a bit and try again")
                # we should wait a couple seconds and try again.
                time.sleep(5)
                cls.destroy_security_group(name)
            else:
                print(f"Unhandled error: {e.response['Error']['Code']}")
            return
        print("Deleted security group.")
        return
