#!/bin/bash 
# This script resets a deployment to ensure that we can update a greengrass group

GG_GROUP_ID=$(aws greengrass list-groups --query "Groups[?Name=='gg_ml_sample']".Id --output=text)
if ! [ -z "${GG_GROUP_ID}" ]; then
   echo "Resetting deployment for id ${GG_GROUP_ID}"
   aws greengrass reset-deployments --group-id ${GG_GROUP_ID} --force
   sleep 5
fi