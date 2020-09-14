#!/bin/bash 
[ -z "$1" ] && echo "Please provide a deployment bucket name" && exit 1

if ! aws s3 ls "s3://$1" > /dev/null 2>&1; then
  echo "Creating bucket for deployment: $1" 
  if ! aws s3 mb "s3://$1" ; then
    echo "Could not create bucket $1. Please specify a different name" 
    exit 1
  fi
fi