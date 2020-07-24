#!/bin/bash 
[ -z "$1" ] && echo "Please prove greengrass group name as parameter" && exit 1

GG_GROUP_NAME="$1"

GG_GROUP_ID=$(aws greengrass list-groups --query "Groups[?Name=='${GG_GROUP_NAME}']".Id --output=text)
# get latest version id
GROUP_VERSION_ID=$(aws greengrass list-group-versions --group-id ${GG_GROUP_ID} --query 'Versions[0].Version')
# strip double quotes
GROUP_VERSION_ID=$(echo $GROUP_VERSION_ID | tr -d '"')
# start deployment
aws greengrass create-deployment --group-id ${GG_GROUP_ID} --group-version-id ${GROUP_VERSION_ID} --deployment-type NewDeployment