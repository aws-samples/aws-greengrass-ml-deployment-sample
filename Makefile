# This is the EC2 Key pair name which can be used to connect to the greengrass core
KEY_PAIR_NAME=iot-ml-sample
# This is the corresponding EC2 Key pair file location on your local disk
KEY_PAIR_FILE=~/.ssh/iot-ml-sample.pem

######################################
# Do not change below unless required#
######################################

# This is the bucket where AWS SAM will upload its deployment packages
DEPLOYMENT_BUCKET="ml-gg-deployment-sample-$(shell aws sts get-caller-identity --query "Account" --output=text)"
# This is the bucket storing the ML_resources
ML_RESOURCE_BUCKET="ml-gg-deployment-sample"
MODEL_PACKAGE_TF_FULL="s3://${ML_RESOURCE_BUCKET}/models/mobilenet-keras-with-libs/model-package.tar.gz"
MODEL_PACKAGE_NEO="s3://${ML_RESOURCE_BUCKET}/models/mobilenet-neo/model-ml_c5.tar.gz"


deploy: build
	scripts/ensure_deployment_bucket_exists.sh ${DEPLOYMENT_BUCKET}
	scripts/reset_deployment.sh
	sam deploy --s3-bucket ${DEPLOYMENT_BUCKET} --parameter-overrides "MLResourceLocationTFFull=${MODEL_PACKAGE_TF_FULL} MLResourceLocationNeo=${MODEL_PACKAGE_NEO} myKeyPair=${KEY_PAIR_NAME}"
	scripts/create_deployment.sh gg_ml_sample

build:
	sam build --use-container

destroy:
	aws cloudformation delete-stack --stack-name gg-ml-sample
	aws cloudformation wait stack-delete-complete \
    --stack-name gg-ml-sample

ssh:
	scripts/ssh_gg_instance.sh ${KEY_PAIR_NAME} ${KEY_PAIR_FILE}