GG_GROUP_NAME="gg_ml_sample"
MODEL_PACKAGE="s3://ml-gg-deployment-sample/models/image-net-tf-lite-20-08-19-12-41-49/model.tar.gz"
MODEL_PACKAGE_TF_FULL="s3://ml-gg-deployment-sample/models/image-net-tf-full-20-08-19-12-42-57/model-package.tar.gz"
MY_KEY_PAIR=iot-ml-sample

deploy:
	scripts/reset_deployment.sh
	sam build && sam deploy --parameter-overrides "MLResourceLocationTFLite=${MODEL_PACKAGE} MLResourceLocationTFFull=${MODEL_PACKAGE_TF_FULL} myKeyPair=${MY_KEY_PAIR}"
	scripts/create_deployment.sh ${GG_GROUP_NAME}

destroy:
	aws cloudformation delete-stack --stack-name gg-ml-sample
	aws cloudformation wait stack-delete-complete \
    --stack-name gg-ml-sample

ssh:
	scripts/ssh_gg_instance.sh