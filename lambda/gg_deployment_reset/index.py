import os
import sys
import json
import logging
import boto3
from botocore.exceptions import ClientError
import cfnresponse

lgr = logging.getLogger()
lgr.setLevel(logging.INFO)

c = boto3.client("greengrass")
iam = boto3.client("iam")
role_name = "greengrass_cfn_{}_ServiceRole".format(os.environ["STACK_NAME"])
policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGreengrassResourceAccessRolePolicy"
policy_arn_s3 = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"

def find_group(thingName):
    res_auth = ""
    response = c.list_groups()
    for grp in response["Groups"]:
        thingfound = False
        group_version = c.get_group_version(
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
            response_core_version = c.get_core_definition_version(
                CoreDefinitionId=core_id, CoreDefinitionVersionId=core_version_id
            )
            if "Cores" in response_core_version["Definition"]:
                for thing_arn in response_core_version["Definition"]["Cores"]:
                    if thingName == thing_arn["ThingArn"].split("/")[1]:
                        thingfound = True
                        break
        if thingfound:
            lgr.info("found thing: %s, group id is: %s" %
                     (thingName, grp["Id"]))
            res_auth = grp["Id"]
            return res_auth


def manage_role(cmd):
    if cmd == "CREATE":
        r = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument='{"Version": "2012-10-17","Statement": [{"Effect": "Allow","Principal": {"Service": "greengrass.amazonaws.com"},"Action": "sts:AssumeRole"}]}',
            Description="CFN blog post",
        )
        role_arn = r["Role"]["Arn"]
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn,
        )
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn_s3,
        )
        c.associate_service_role_to_account(RoleArn=role_arn)
        lgr.info("Created/assoc role {}".format(role_name))
    else:
        try:
            r = iam.get_role(RoleName=role_name)
            role_arn = r["Role"]["Arn"]
            c.disassociate_service_role_from_account()
            iam.detach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn,
            )
            iam.detach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn_s3,
            )
            iam.delete_role(RoleName=role_name)
            lgr.info("Deleted service role {}".format(role_name))
        except ClientError as e:
            lgr.error("No service role to delete: %s" % e)
            return True
    return True


def handler(event, context):
    responseData = {}
    try:
        lgr.info("Received event: {}".format(json.dumps(event)))
        res = cfnresponse.FAILED
        thingName = event["ResourceProperties"]["ThingName"]
        if event["RequestType"] == "Create":
            try:
                c.get_service_role_for_account()
                res = cfnresponse.SUCCESS
            except ClientError as e:
                manage_role("CREATE")
                lgr.info("GG service role created")
                res = cfnresponse.SUCCESS
        elif event["RequestType"] == "Delete":
            gid = find_group(thingName)
            lgr.info("Group id to delete: %s" % gid)
            if gid:
                c.reset_deployments(Force=True, GroupId=gid)
                lgr.info("Forced reset of deployment")
                if manage_role("DELETE"):
                    res = cfnresponse.SUCCESS
                    lgr.info("Service role deleted")
            else:
                lgr.error("No group: %s found" % thingName)
    except ClientError as e:
        lgr.error("Error: %s" % e)
        res = cfnresponse.FAILED
    lgr.info("Response of: %s, with result of: %s" % (res, responseData))
    sys.stdout.flush()
    cfnresponse.send(event, context, res, responseData)
