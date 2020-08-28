BUCKET="ml-gg-deployment-sample"
MY_KEY_PAIR=iot-ml-sample
MY_KEY_File=~/.ssh/iot-ml-sample-.pem

# Do not change unless you specified a different location during build
MODEL_PACKAGE_TF_FULL="s3://${BUCKET}/models/mobilenet-keras-with-libs/model-package.tar.gz"
MODEL_PACKAGE_NEO="s3://${BUCKET}/models/mobilenet-neo/model-ml_c5.tar.gz"



build:
	sam build --use-container

deploy: build
	scripts/reset_deployment.sh
	sam deploy --s3-bucket ${BUCKET} --parameter-overrides "MLResourceLocationTFFull=${MODEL_PACKAGE_TF_FULL} MLResourceLocationNeo=${MODEL_PACKAGE_NEO} myKeyPair=${MY_KEY_PAIR}"
	scripts/create_deployment.sh gg_ml_sample

destroy:
	aws cloudformation delete-stack --stack-name gg-ml-sample
	aws cloudformation wait stack-delete-complete \
    --stack-name gg-ml-sample

ssh:
	scripts/ssh_gg_instance.sh ${MY_KEY_File}