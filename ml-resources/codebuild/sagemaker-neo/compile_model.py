import time
import os
import sagemaker
from sagemaker.utils import name_from_base
import boto3

BUCKET = os.getenv('BUILD_ARTIFACT_BUCKET')
print("Artifact bucket:"+ BUCKET)

account_id = boto3.client('sts').get_caller_identity().get('Account')
role = f"arn:aws:iam::{account_id}:role/NeoCompilationRole"
sess = sagemaker.Session()
region = sess.boto_region_name
sm_client = boto3.client('sagemaker')

# create job name with timestamp
compilation_job_name = name_from_base('tf-mobilenetv2-neo')
data_shape = '{"input_1":[1,3,224,224]}'
target_device = 'ml_c5'
framework = 'KERAS'
framework_version = '2.3.1'
compiled_model_path = 's3://{}/models/mobilenet-neo/'.format(BUCKET, compilation_job_name)
model_path = 's3://{}/{}'.format(BUCKET, "models/mobilenet-keras/model.tar.gz")

response = sm_client.create_compilation_job(
    CompilationJobName=compilation_job_name,
    RoleArn=role,
    InputConfig={
        'S3Uri': model_path,
        'DataInputConfig': data_shape,
        'Framework': framework
    },
    OutputConfig={
        'S3OutputLocation': compiled_model_path,
        'TargetDevice': target_device
    },
    StoppingCondition={
        'MaxRuntimeInSeconds': 300
    }
)
print(response)

# Poll every 30 sec
while True:
    response = sm_client.describe_compilation_job(CompilationJobName=compilation_job_name)
    if response['CompilationJobStatus'] == 'COMPLETED':
        break
    elif response['CompilationJobStatus'] == 'FAILED':
        raise RuntimeError('Compilation failed')
    print('Compiling ...')
    time.sleep(30)
print('Done!')

compiled_model_path = response['ModelArtifacts']['S3ModelArtifacts']
print("Compiled model available at:" + compiled_model_path)
