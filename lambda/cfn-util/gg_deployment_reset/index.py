"""
This lambda function controls a cloudformation custom resource which ensures greengrass has a service role with necessary permissions attached on stack creation.
In addition it ensures greengrass deployment is reset on stack deletion and the role is deleted as well.

NOTE: The role has elevated permissions and should be scoped down for production use!
"""

import os
import sys
import json
import logging
import boto3
from botocore.exceptions import ClientError
import cfnresponse

# Role name to be attached to Greengrass
ROLE_NAME = "greengrass_cfn_{}_ServiceRole".format(os.environ["STACK_NAME"])
# The policies to be attached to the role
POLICY_ARN = "arn:aws:iam::aws:policy/service-role/AWSGreengrassResourceAccessRolePolicy"
POLICY_ARN_S3 = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"


lgr = logging.getLogger()
lgr.setLevel(logging.INFO)
greengrass = boto3.client("greengrass")
iam = boto3.client("iam")


def find_group(thing_name):
    """
       Returns the Greengrass group for the given core thing name
    """
    res_auth = ""
    response = greengrass.list_groups()
    for grp in response["Groups"]:
        thingfound = False
        group_version = greengrass.get_group_version(
            GroupId=grp["Id"], GroupVersionId=grp["LatestVersion"]
        )

        core_arn = group_version["Definition"].get(
            "CoreDefinitionVersionArn", "")
        if core_arn:
            core_id = core_arn[
                core_arn.index("/cores/") + 7: core_arn.index("/versions/")
            ]
            core_version_id = core_arn[
                core_arn.index("/versions/") + 10: len(core_arn)
            ]
            thingfound = False
            response_core_version = greengrass.get_core_definition_version(
                CoreDefinitionId=core_id, CoreDefinitionVersionId=core_version_id
            )
            if "Cores" in response_core_version["Definition"]:
                for thing_arn in response_core_version["Definition"]["Cores"]:
                    if thing_name == thing_arn["ThingArn"].split("/")[1]:
                        thingfound = True
                        break
        if thingfound:
            lgr.info("found thing: %s, group id is: %s" %
                     (thing_name, grp["Id"]))
            res_auth = grp["Id"]
            return res_auth


def manage_role(cmd):
    """
       On stack creation creates the necessary greengrass role required for group deployment. On stack delete role will also be deleted!
    """
    if cmd == "CREATE":
        role = iam.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument='{"Version": "2012-10-17","Statement": [{"Effect": "Allow","Principal": {"Service": "greengrass.amazonaws.com"},"Action": "sts:AssumeRole"}]}',
            Description="CFN blog post",
        )
        role_arn = role["Role"]["Arn"]
        iam.attach_role_policy(
            RoleName=ROLE_NAME,
            PolicyArn=POLICY_ARN,
        )
        iam.attach_role_policy(
            RoleName=ROLE_NAME,
            PolicyArn=POLICY_ARN_S3,
        )
        greengrass.associate_service_role_to_account(RoleArn=role_arn)
        lgr.info("Created/assoc role %s", ROLE_NAME)
    else:
        try:
            role = iam.get_role(RoleName=ROLE_NAME)
            role_arn = role["Role"]["Arn"]
            greengrass.disassociate_service_role_from_account()
            iam.detach_role_policy(
                RoleName=ROLE_NAME,
                PolicyArn=POLICY_ARN,
            )
            iam.detach_role_policy(
                RoleName=ROLE_NAME,
                PolicyArn=POLICY_ARN_S3,
            )
            iam.delete_role(RoleName=ROLE_NAME)
            lgr.info("Deleted service role %s", ROLE_NAME)
        except ClientError as error:
            lgr.error("No service role to delete: %s", error)
            return True
    return True


def handler(event, context):
    """
       Create and attach greengrass role on create.
       Delete role and reset greengrass deployment on delete!
    """
    response_data = {}
    try:
        lgr.info("Received event: %s", json.dumps(event))
        res = cfnresponse.FAILED
        thing_name = event["ResourceProperties"]["ThingName"]
        if event["RequestType"] == "Create":
            try:
                greengrass.get_service_role_for_account()
                res = cfnresponse.SUCCESS
            except ClientError:
                manage_role("CREATE")
                lgr.info("GG service role created")
                res = cfnresponse.SUCCESS
        elif event["RequestType"] == "Delete":
            gid = find_group(thing_name)
            lgr.info("Group id to delete: %s", gid)
            if gid:
                greengrass.reset_deployments(Force=True, GroupId=gid)
                lgr.info("Forced reset of deployment")
                if manage_role("DELETE"):
                    res = cfnresponse.SUCCESS
                    lgr.info("Service role deleted")
            else:
                lgr.error("No group: %s found", thing_name)
    except ClientError as error:
        lgr.error("Error: %s", error)
        res = cfnresponse.FAILED
    lgr.info("Response of: %s, with result of: %s", res, response_data)
    sys.stdout.flush()
    cfnresponse.send(event, context, res, response_data)
