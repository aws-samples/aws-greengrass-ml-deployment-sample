GG_GROUP_NAME="gg_ml_sample"
MODEL_PACKAGE_TF_FULL="s3://ml-gg-deployment-sample/models/image-net-tf-full-20-08-27-12-31-28/model-package.tar.gz"
MODEL_PACKAGE_NEO="s3://ml-gg-deployment-sample/models/mobilenet-neo/model-ml_c5.tar.gz"
MY_KEY_PAIR=iot-ml-sample


build:
	sam build --use-container
	cp .aws-sam/build/ImageClassifierFunctionNeo/dlr-1.1.data/data/dlr/libdlr.so .aws-sam/build/ImageClassifierFunctionNeo/dlr/


deploy: build
	scripts/reset_deployment.sh
	sam deploy --parameter-overrides "MLResourceLocationTFFull=${MODEL_PACKAGE_TF_FULL} MLResourceLocationNeo=${MODEL_PACKAGE_NEO} myKeyPair=${MY_KEY_PAIR}"
	scripts/create_deployment.sh ${GG_GROUP_NAME}

destroy:
	aws cloudformation delete-stack --stack-name gg-ml-sample
	aws cloudformation wait stack-delete-complete \
    --stack-name gg-ml-sample

ssh:
	scripts/ssh_gg_instance.sh