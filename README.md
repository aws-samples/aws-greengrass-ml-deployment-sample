# Deployment options for machine learning inference on AWS Greengrass

## Introduction

This repository provides an overview of deployment options for a machine learning inference on AWS Greengrass. It includes both an overview of available options and underlying concepts, and a practical implementation sample.

## Performing ML inference at the edge with AWS IoT Greengrass

With AWS IoT Greengrass, you can [perform machine learning (ML) inference at the edge](https://docs.aws.amazon.com/greengrass/latest/developerguide/ml-inference.html) on locally generated data using cloud-trained models. You benefit from the low latency and cost savings of running local inference, yet still take advantage of cloud computing power for training models and complex processing.

In order to perform ML inference at the edge with [AWS IoT Greengrass](https://aws.amazon.com/greengrass/) you need to deploy 3 components on the Greengrass device:

1. A trained machine learning (ML) model
2. An inference code
3. Machine learning libraries required for inference, like Tensorflow, Pytorch or the [Amazon SageMaker Neo deep learning runtime](https://docs.aws.amazon.com/greengrass/latest/developerguide/ml-inference.html#dlc-optimize-info)

Each of these components has different requirements in terms of storage and update frequency:

| Part               | Typical size      | Update demand frequency                   |
| ------------------ | ----------------- | ----------------------------------------- |
| 1. ML model        | few MB up to a GB | medium to high (depending on model decay) |
| 2. Inference logic | usually few KB    | medium                                    |
| 3. ML Libraries    | up to several Gb  | low (new versions, security fixes)        |

Depending on size and and update frequency demand there are several option you can pick for deployment for each of these components.

### Deploying the trained ML Model

The machine learning model can be included as part of the lambda function deployment package itself or deployed using a ["ML resources"](https://docs.aws.amazon.com/greengrass/latest/developerguide/ml-inference.html) in AWS Greengrass.

Using ML resources is usually the preferred, as:

- The model is or can get to big to fit in the maximum deployment package size of a lambda function (50 MB zipped)
- The model should typically be updated independent of the lambda function code

### Deploying the inference logic

The inference code itself is deployed as part of the AWS Lambda function. It uses a machine learning library to call the model for inference and returns the results as required within the business context. In a production setting the deployment of the lambda function should be automated ideally using infrastructure as code (IaC). A common tool particularly when automating the deployment of lambda functions is [AWS SAM](https://github.com/awslabs/serverless-application-model).
AWS SAM makes it easy to organize all required resources in a single stack and has a lot of best-practices for deployment built-in.

### Deploying machine learning libraries

In order to get predictions from a model within your inference code you require the necessary machine learning library. This is typically a machine learning library optimized for inference at the edge like the [Amazon SageMaker Neo deep learning runtime](https://docs.aws.amazon.com/greengrass/latest/developerguide/ml-inference.html#dlc-optimize-info) or [Tensorflow Lite](https://www.tensorflow.org/lite).
These libraries are small in size and can be included as part of the lambda deployment package.

However not all model architectures are supported by these edge optimized inference libraries. It is not uncommon to require a full distribution of [Tensorflow](https://www.tensorflow.org/), [Pytorch](https://pytorch.org/) or [MXNet](https://mxnet.apache.org/) to be deployed on the edge device. These libraries can be several hundred MB in size, which makes them impossible to be included in the AWS Lambda deployment package.

There are two ways to deal with these large libraries during deployment:

- Deploy ML libraries on OS level on the Greengrass core
- Deploy ML libraries using a [Greengrass ML resource](https://docs.aws.amazon.com/greengrass/latest/developerguide/ml-inference.html)

#### Installing ML libraries on OS level

A typical way this is done is using the OS or language specific package manager, e.g. using the system python package manager:

```bash
pip install tensorflow
```

This comes with two big disadvantages:

- the deployment of the libraries is decoupled from the standard [Greengrass group deployment process](https://docs.aws.amazon.com/greengrass/latest/developerguide/deployments.html)
- the deployment requires a separate custom agent on the device or remote OS access to perform the installation and required updates

#### Installing ML libraries using Greegrass ML resources

Another option is to bundle required libraries and use ["ML resources"](https://docs.aws.amazon.com/greengrass/latest/developerguide/ml-inference.html) during deployment and load the libraries dynamically
on function startup. In Python this can be achieved in two ways:

- by setting the PYTHONPATH environment variable to the location of the ML resource (Containerized lambda functions only).
- or by dynamically appending the location of the libraries to the Python system path (non-containerized lambda functions):

```python
import sys
import os

resourcePath = os.getenv("AWS_GG_RESOURCE_PREFIX")
python_pkg_path = os.path.join(
    resourcePath, "<path_to_dependencies>")
sys.path.append(python_pkg_path)
```

This allows you to deploy machine earning libraries as part of the standard Greengrass deployment process and has no limitation on the maximum size of the libraries imposed by the deployment process.

#### How it works in detail

The content of the file referenced in the ML resource containing the pre-built libraries will be transferred from an Amazon S3 bucket to your Greengrass devices and unpackaged in a local directory. As the AWS Lambda ML inference function starts, AWS IoT Greengrass core will mount the local directory with unpackaged contents of the file to a local directory in the Lambda container e.g. `/mllibs`.

The Python interpreter then uses the environment variable PYTHONPATH to look for and load available libraries. If you configure PYTHONPATH in GG Group Lambda config, it‘s prepended to an actual PYTHONPATH, e.g. if PYTHONPATH=„/mllibs“ in GG group Lambda settings the PYTHONPATH is „/mllibs:/lamba“ during Lambda execution

## Implementation sample

To run the sample you have two option: deplyoing via SAM / CloudFormation or following step-by-step guidelines for AWS console. Each of these options is described in following chapters

### Deploying sample via SAM / AWS CloudFormation

Install docker

```
git clone bla
make build
make deploy
```

### Step-by-step guidelines for AWS console

#### Preparation

#### Part 1: Preparing a ML library deployment

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
