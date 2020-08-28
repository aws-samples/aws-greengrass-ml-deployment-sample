BUCKET_NAME="ml-gg-deployment-sample"

deploy: deployCodeBuildStack run

run: uploadScript runBuild
	
deployCodeBuildStack:
	echo "Deploying codebuild cloudformation stack"
	aws cloudformation deploy --template template.yaml --stack-name build-model --capabilities "CAPABILITY_IAM" --parameter-overrides "BucketName=${BUCKET_NAME}"

uploadScript:
	aws s3 sync codebuild/ s3://${BUCKET_NAME}/codebuild/

runBuild:
	echo "Running Build to create model"
	aws codebuild start-build --project-name PackageModelTFFull --query "build.id" --output=text
	aws codebuild start-build --project-name PackageModelTFLite --query "build.id" --output=text

logs:
	aws logs tail /aws/codebuild --follow --since 20s 

destroy:
	aws cloudformation delete-stack --stack-name build-model
	aws cloudformation wait stack-delete-complete \
    --stack-name build-model