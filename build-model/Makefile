BUCKET_NAME="ml-deployment-828266890613"

deploy: deployCodeBuildStack uploadScript 

run: uploadScript runBuild
	
destroy:
	aws cloudformation delete-stack --stack-name build-model
	aws cloudformation wait stack-delete-complete \
    --stack-name build-model

deployCodeBuildStack:
	aws cloudformation deploy --template template.yaml --stack-name build-model --capabilities "CAPABILITY_IAM" --parameter-overrides "BucketName=${BUCKET_NAME}"

uploadScript:
	aws s3 sync codebuild/ s3://${BUCKET_NAME}/codebuild/

runBuild:
	aws codebuild start-build --project-name PackageModel --query "build.id" --output=text
	aws logs tail /aws/codebuild/PackageModel --follow --since 20s 