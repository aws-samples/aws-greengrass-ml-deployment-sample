# This is the bucket where AWS SAM will upload its deployment packages
DEPLOYMENT_BUCKET="<bucket-name>"
# This is the EC2 Key pair name which can used to connect to the greengrass core
MY_KEY_PAIR=<key-pair-name>
# This is the corresponding EC2 Key pair file location on your local disk
MY_KEY_File=~/.ssh/<my-key>.pem

# Do not change below unless you want to specify a different lcoation for the ml_resources
ML_RESOURCE_BUCKET="ml-gg-deployment-sample"
MODEL_PACKAGE_TF_FULL="s3://${ML_RESOURCE_BUCKET}/models/mobilenet-keras-with-libs/model-package.tar.gz"
MODEL_PACKAGE_NEO="s3://${ML_RESOURCE_BUCKET}/models/mobilenet-neo/model-ml_c5.tar.gz"

deploy: build
	scripts/reset_deployment.sh
	sam deploy --s3-bucket ${DEPLOYMENT_BUCKET} --parameter-overrides "MLResourceLocationTFFull=${MODEL_PACKAGE_TF_FULL} MLResourceLocationNeo=${MODEL_PACKAGE_NEO} myKeyPair=${MY_KEY_PAIR}"
	scripts/create_deployment.sh gg_ml_sample

build:
	sam build --use-container

destroy:
	aws cloudformation delete-stack --stack-name gg-ml-sample
	aws cloudformation wait stack-delete-complete \
    --stack-name gg-ml-sample

ssh:
	scripts/ssh_gg_instance.sh ${MY_KEY_File}