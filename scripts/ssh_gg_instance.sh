#!/bin/bash


PUBLIC_IP=$(aws ec2 describe-instances \
  --query "Reservations[*].Instances[?KeyName=='iot-ml-sample'].PublicIpAddress" \
  --output=text)

ssh -i ${1} ubuntu@$PUBLIC_IP