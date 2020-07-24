#!/bin/bash

PUBLIC_IP=$(aws ec2 describe-instances \
  --query "Reservations[*].Instances[?KeyName=='iot-ml-sample'].PublicIpAddress" \
  --output=text)

ssh -i ~/.ssh/iot-ml-sample.pem ubuntu@$PUBLIC_IP