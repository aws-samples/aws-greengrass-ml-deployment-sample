#!/bin/bash 
# This script creates a greengrass deployment and waites until deployment is finished

[ -z "$1" ] && echo "Please provide greengrass group name as parameter" && exit 1
GG_GROUP_NAME="$1"

GG_GROUP_ID=$(aws greengrass list-groups --query "Groups[?Name=='${GG_GROUP_NAME}']".Id --output=text)
# get latest version id
GROUP_VERSION_ID=$(aws greengrass list-group-versions --group-id ${GG_GROUP_ID} --query 'Versions[0].Version')
# strip double quotes
GROUP_VERSION_ID=$(echo $GROUP_VERSION_ID | tr -d '"')
# start deployment
DEPLOYMENT_ID=$(aws greengrass create-deployment --group-id ${GG_GROUP_ID} --group-version-id ${GROUP_VERSION_ID} --deployment-type NewDeployment  --query 'DeploymentId' --output=text)

# Wait for deployment to finish
while true
do
  DEPLOY_STATUS=$(aws greengrass get-deployment-status --deployment-id "$DEPLOYMENT_ID" --group-id "$GG_GROUP_ID" --query 'DeploymentStatus' --output=text)
  echo "Current Deployment status is $DEPLOY_STATUS"
  if [ ! "$DEPLOY_STATUS" == "Building" ] && [ ! "$DEPLOY_STATUS" == "InProgress" ];then
   
   echo "Finished deployment with status $DEPLOY_STATUS" && exit
  fi
sleep 5
done