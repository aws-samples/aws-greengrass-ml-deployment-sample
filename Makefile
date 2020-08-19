GG_GROUP_NAME="gg_ml_sample"

deploy:
	scripts/reset_deployment.sh
	sam build && sam deploy
	scripts/deploy_gg.sh ${GG_GROUP_NAME}

destroy:
	aws cloudformation delete-stack --stack-name gg-ml-sample
	aws cloudformation wait stack-delete-complete \
    --stack-name gg-ml-sample

ssh:
	scripts/ssh_gg_instance.sh