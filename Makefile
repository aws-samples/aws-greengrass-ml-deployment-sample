GG_GROUP_NAME="gg_ml_sample"
MODEL_PACKAGE="s3://ml-deployment-828266890613/models/image-net-tf-lite-20-08-19-09-20-27/model.tar.gz"

deploy:
	scripts/reset_deployment.sh
	sam build && sam deploy --parameter-overrides "MLResourceLocation=${MODEL_PACKAGE}"
	scripts/create_deployment.sh ${GG_GROUP_NAME}

destroy:
	aws cloudformation delete-stack --stack-name gg-ml-sample
	aws cloudformation wait stack-delete-complete \
    --stack-name gg-ml-sample

ssh:
	scripts/ssh_gg_instance.sh