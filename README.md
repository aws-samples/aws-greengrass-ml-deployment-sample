# Deployment and maintanance of ML libraries on an AWS IoT Greengrass device

This sample provides an overview of options and reusable components for deployment&maintanance of ML models on an AWS IoT Greengrass device.

The code examples assumes usage of a Python as a programming language for performing inference.

## Introduction

With AWS IoT Greengrass, you can [perform machine learning (ML) inference at the edge](https://docs.aws.amazon.com/greengrass/latest/developerguide/ml-inference.html) on locally generated data using cloud-trained models. You benefit from the low latency and cost savings of running local inference, yet still take advantage of cloud computing power for training models and complex processing.

[AWS IoT Greengrass](https://aws.amazon.com/greengrass/) supports performing a ML inference at the edge by providing three capabilites:

- Deploy ML models by using ["ML resources"](https://docs.aws.amazon.com/greengrass/latest/developerguide/ml-inference.html)
- Deplo an inference logic, with two options:
  - Deploy [AWS pre-built ML connectors](https://docs.aws.amazon.com/greengrass/latest/developerguide/connectors-list.html) with an inference logic
  - Deploying custom-built [AWS Lambda functions](https://docs.aws.amazon.com/greengrass/latest/developerguide/access-ml-resources.html) with inference logic

When deploying custom-built AWS Lambda functions for performing an ML inference, two components must be deployed and maintaned on a Greengrass devcie:

- Component 1: A set of ML libraries neccessary for inference execution (e.g. Tensorflow, Keras, Numpy, Pandas, scipy, soundfile).
- Component 2: Inference logic, i.e. commands to calling APIs of ML libraries and interpretation of these commands in context of a specific use-case

Comparison of both components shows differencies regarding storage size and update demand frequency:

| Part               | Typical size     | Update demand frequency          |
| ------------------ | ---------------- | -------------------------------- |
| 1. ML Libraries    | up to several Gb | low (for new libraries releases) |
| 2. Inference logic | Kb               | high                             |

Based on this observation, a frequent requirement is an ability to decouple deployment of the inference logic from the deployment of ML libraries, while keeping existing cloud-based toolchain for management for both inference logic and ML libraries.

This document describes options for an implementation of this requirement.

## Options

This chapter provides an overview of available options and compares them.

### 1. Using "Machine learning resources" of AWS IoT Greengrass to deploy ML libraries

In AWS IoT Greengrass, ["Machine learning resources"](https://docs.aws.amazon.com/greengrass/latest/developerguide/ml-inference.html) represent cloud-trained inference models that are deployed to an AWS IoT Greengrass core. AWS IoT Greengrass supports Amazon SageMaker and Amazon S3 model sources for machine learning resources.

In this option, we are making use of "Machine learning resources" with Amazon S3 as a source to deploy ML libraries instead of ML models.

### Implementation steps

For a sake of better understanding, the following explanation describes neccessary steps in AWS management console. Automation possibilities will be described in next chapters.

#### Part 1: preparing a ML library deployment

1. Store the ML libraries to be used for ML inference as a .zip file in an Amazon S3 bucket of your choice. We will use a name "mllibraries.zip" in this example.

   **Please note that the libraries should be compatible to a Greengrass device.**

#### Part 2: Configuring machine learning resource

1. Switch to a relevant AWS IoT Greengrass group and click on "Resources" section

2. Choose "Machine learning" and click on "Add a machine learning resource"

3. Select resource name, for example `mllibs`

4. For "model source", select a path to an Amazon S3 bucket and a .zip file you used in step 1.

5. For "local path" please select a path which your AWS Lambda ML inference function will be using to access the deployed ML libraries, for example `/mllibs`

6. For "Lambda function affiliations", please select an AWS Lambda ML inference function which needs the ML libraries in "mllibraries.zip"

7. Click on save

#### Part 3: Configuring AWS Lambds function in a Greengrass group

1. Switch to a relevant AWS IoT Greengrass group and click on "Lambdas" section
2. Select an AWS Lambda ML inference function which needs the ML libraries in "mllibraries.zip"
3. In section "Environment variables", set a variable PYTHONPATH to a value `/mllibs` (or any other value you chose in step 5 of part 2)

#### Part 4: Deploy a Greengrass group

1. Redeploy a Greengrass group.
2. Now your AWS Lambda ML inference function is able to load the neccessary ML libraries.

### Technical background

The content of "mllibraries.zip" file will be transferred from an Amazon S3 bucket to your Greengrass devices and unpackaged in a local directory. As the AWS Lambda ML inference function starts, AWS IoT Greengrass core will mount the local directory with unpackaged "mllibraries.zip" to a `/mllibs` directory in Lambdas's container

Python interpreter uses environment variable PYTHONPATH to look for available libraries. If you configure PYTHONPATH in GG Group Lambda config, it‘s prepended to an actual PYTHONPATH, e.g. if PYTHONPATH=„/mllibs“ in GG group Lambda settings the PYTHONPATH is „/mllibs:/lamba“ during Lambda execution

#### Limitations

- Works only for contanerized AWS Lambda functions

### END OF CONTENT! END OF CONTENT!END OF CONTENT!END OF CONTENT!END OF CONTENT!END OF CONTENT!END OF CONTENT!

### END OF CONTENT! END OF CONTENT!END OF CONTENT!END OF CONTENT!END OF CONTENT!END OF CONTENT!END OF CONTENT!

### END OF CONTENT! END OF CONTENT!END OF CONTENT!END OF CONTENT!END OF CONTENT!END OF CONTENT!END OF CONTENT!

### END OF CONTENT! END OF CONTENT!END OF CONTENT!END OF CONTENT!END OF CONTENT!END OF CONTENT!END OF CONTENT!

### END OF CONTENT! END OF CONTENT!END OF CONTENT!END OF CONTENT!END OF CONTENT!END OF CONTENT!END OF CONTENT!

### END OF CONTENT! END OF CONTENT!END OF CONTENT!END OF CONTENT!END OF CONTENT!END OF CONTENT!END OF CONTENT!

### 2. Install ML libs on OS level in „/abc/libs“, create an volume ressource in GG Group pointing to „/abc/libs“

## Technical background

### PYTHONPATH environment variable on AWS IoT Greengrass Lambda

P

## Comparison

| Option      | Criteria 1 | Criteria 2 |
| ----------- | ---------- | ---------- |
| 1. Option 1 |            |            |
| 2. Option 2 |            |            |

## Other related services

## Conclusion and further reading

# greengrass-ml-sample-app

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- hello_world - Code for the application's Lambda function.
- events - Invocation events that you can use to invoke the function.
- tests - Unit tests for the application code.
- template.yaml - A template that defines the application's AWS resources.

The application uses several AWS resources, including Lambda functions and an API Gateway API. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.

If you prefer to use an integrated development environment (IDE) to build and test your application, you can use the AWS Toolkit.  
The AWS Toolkit is an open source plug-in for popular IDEs that uses the SAM CLI to build and deploy serverless applications on AWS. The AWS Toolkit also adds a simplified step-through debugging experience for Lambda function code. See the following links to get started.

- [PyCharm](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
- [IntelliJ](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
- [VS Code](https://docs.aws.amazon.com/toolkit-for-vscode/latest/userguide/welcome.html)
- [Visual Studio](https://docs.aws.amazon.com/toolkit-for-visual-studio/latest/user-guide/welcome.html)

## Deploy the sample application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

- SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- [Python 3 installed](https://www.python.org/downloads/)
- Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build --use-container
sam deploy --guided
```

The first command will build the source of your application. The second command will package and deploy your application to AWS, with a series of prompts:

- **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
- **AWS Region**: The AWS region you want to deploy your app to.
- **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
- **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modified IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
- **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

You can find your API Gateway Endpoint URL in the output values displayed after deployment.

## Use the SAM CLI to build and test locally

Build your application with the `sam build --use-container` command.

```bash
greengrass-ml-sample-app$ sam build --use-container
```

The SAM CLI installs dependencies defined in `hello_world/requirements.txt`, creates a deployment package, and saves it in the `.aws-sam/build` folder.

Test a single function by invoking it directly with a test event. An event is a JSON document that represents the input that the function receives from the event source. Test events are included in the `events` folder in this project.

Run functions locally and invoke them with the `sam local invoke` command.

```bash
greengrass-ml-sample-app$ sam local invoke HelloWorldFunction --event events/event.json
```

The SAM CLI can also emulate your application's API. Use the `sam local start-api` to run the API locally on port 3000.

```bash
greengrass-ml-sample-app$ sam local start-api
greengrass-ml-sample-app$ curl http://localhost:3000/
```

The SAM CLI reads the application template to determine the API's routes and the functions that they invoke. The `Events` property on each function's definition includes the route and method for each path.

```yaml
Events:
  HelloWorld:
    Type: Api
    Properties:
      Path: /hello
      Method: get
```

## Add a resource to your application

The application template uses AWS Serverless Application Model (AWS SAM) to define application resources. AWS SAM is an extension of AWS CloudFormation with a simpler syntax for configuring common serverless application resources such as functions, triggers, and APIs. For resources not included in [the SAM specification](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md), you can use standard [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html) resource types.

## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
greengrass-ml-sample-app$ sam logs -n HelloWorldFunction --stack-name greengrass-ml-sample-app --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Unit tests

Tests are defined in the `tests` folder in this project. Use PIP to install the [pytest](https://docs.pytest.org/en/latest/) and run unit tests.

```bash
greengrass-ml-sample-app$ pip install pytest pytest-mock --user
greengrass-ml-sample-app$ python -m pytest tests/ -v
```

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name greengrass-ml-sample-app
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)
