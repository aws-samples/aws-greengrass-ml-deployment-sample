#!/bin/bash
KEY_NAME=$1
KEY_LOCATION=$2

PUBLIC_IP=$(aws ec2 describe-instances \
  --query "Reservations[*].Instances[?KeyName=='${KEY_NAME}'].PublicIpAddress" \
  --output=text)

ssh -i ${KEY_LOCATION} ubuntu@$PUBLIC_IP