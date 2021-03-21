""" ch_delete.py

    This class has several methods that wrap aws api calls, as well as some error handling.
    It inherits from the ch_base class.

"""

import time
import os
from botocore.exceptions import ClientError # type: ignore
from ch_base import CHBase

class CHDelete(CHBase):
    """ All methods of this class delete aws resources or have otherwise destructive functions.

    """
    def __init__(self):
        CHBase.__init__(self)

    @classmethod
    def destroy_role(cls, name: str):
        """ This wraps the iam.delete_role api call and deletes a role with the specified name.

            Args:
                name: the name of the role to be created

        """
        print("Deleting role")
        try:
            cls.iam.delete_role(RoleName=name)
        except ClientError as e:
            if e.response['Error']['Code'] == "NoSuchEntity":
                print("Instance role didn't exist, skip for now.")
            elif e.response['Error']['Code'] == "DeleteConflict":
                print("Role still has policies attached. Remove those and try again.")
            else:
                print(f"Unhandled error: {e.response['Error']['Code']}")
            return

        print("Destroyed role")

    @classmethod
    def detach_role_policy(cls, role_name: str, policy_arn: str):
        """ This wraps the iam.detach_role_policy api call and removes a policy from a role.

            Args:
                role_name: the name of the role the policy is removed from.
                policy_arn: the arn of the policy being detached from the role.

        """
        print("removing policy from role.")

        try:
            cls.iam.detach_role_policy(RoleName=role_name,PolicyArn=policy_arn)
        except ClientError as e:
            if e.response['Error']['Code'] == "NoSuchEntity":
                print("---Policy already removed? skip for now.---")
            else:
                print(f"---Unhandled error: {e.response['Error']['Code']}---")

            return

        print(f"Removed {policy_arn} from {role_name}")

    @classmethod
    def remove_role_from_instance_profile(cls, instance_prof_name: str, role_name: str):
        """ This wraps the iam.remove_role_from_instance_profile api call, which removes a role from
            an instance profile.

            Args:
                instance_prof_name: the name of the instance profile the role is removed from.
                role_name: the name of the role being removed from the instance profile.

        """
        print(f"removing {role_name} from {instance_prof_name}")

        try:
            cls.iam.remove_role_from_instance_profile(InstanceProfileName=instance_prof_name,\
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
        """ This wraps the iam.delete_polcy api call and deletes a custom policy
            with the specified policy name.

            Args:
                policy_name: the name of the policy to be deleted.

        """
        print(f"Deleting policy {policy_arn}")
        try:
            cls.iam.delete_policy(PolicyArn=policy_arn)
        except ClientError as e:
            if e.response['Error']['Code'] == "NoSuchEntity":
                print("Policy didn't exist, skip for now.")
            else:
                print(f"Unhandled error: {e.response['Error']['Code']}")
            return

        print("Destroyed policy")

    @classmethod
    def destroy_instance_profile(cls, name: str):
        """ This wraps the iam.delete_instance_profile api call, which deletes an instance profile.

            Args:
                name: the name of the instance profile to be deleted.

        """
        print("Deleting instance profile")
        try:
            cls.iam.delete_instance_profile(InstanceProfileName=name)
        except ClientError as e:
            if e.response['Error']['Code'] == "NoSuchEntity":
                print("Instance Profile didn't exist, skip for now.")
            else:
                print(f"Unhandled error: {e.response['Error']['Code']}")
            return
        print("Deleted profile")

    @classmethod
    def destroy_instance_key_pair(cls, name: str):
        """ This wraps the ec2.client.delete_key_pair api call, which deletes a key pair.

            This function also deletes a .pem file from the .ssh directory if it exists.

            Args:
                name: the name of the key pair to be deleted.

        """
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
    def destroy_instance(cls, name: str):
        """ This wraps the ec2.resource.Instance.terminate api call, which terminates an instance.

            Args:
                name: the name of the instance being terminated.

        """
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

        print("Terminated Instance")
        return

    @classmethod
    def destroy_security_group(cls, name: str):
        """ This wraps the ec2.client.delete_security_group api call, which deletes a security group

            Args:
                name: the name of the security group to be deleted

        """
        print(f"Deleting security group {name}")
        try:
            cls.ec2client.delete_security_group(GroupName=name)
        except ClientError as e:
            if e.response['Error']['Code'] == "InvalidGroup.NotFound":
                print(f"Security group {name} didn't exist, skip for now.")
            elif e.response['Error']['Code'] == "DependencyViolation":
                print("Security group in use by instance. Maybe it hasn't terminated yet?")
                print("\nWe'll wait a bit and try again")
                # we should wait a couple seconds and try again.
                time.sleep(5)
                cls.destroy_security_group(name)
            else:
                print(f"Unhandled error: {e.response['Error']['Code']}")
            return
        print("Deleted security group.")
        return

    @classmethod
    def destroy_rds_instance(cls, db_instance_id: str):
        """ This wraps the rds.client.delete_db_instance api call.

            Args:
                db_instance_id: the id of the db instance that will be deleted.

        """
        print(f"Terminating rds Instance {db_instance_id}")

        try:
            cls.rds.delete_db_instance(DBInstanceIdentifier=db_instance_id,\
                    SkipFinalSnapshot=True)
        except ClientError as e:
            if e.response['Error']['Code'] == "EntityDoesNotExist":
                print(f"Couldn't terminate instance '{db_instance_id}', skip for now?")
            else:
                print(f"Unhandled error: {e.response['Error']['Code']}")
            return

        print("Terminated rds instance")
        return
