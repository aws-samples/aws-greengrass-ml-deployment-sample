# Deployment options for machine learning inference on AWS Greengrass 

## What is this?

This repository provides an overview of deployment options for machine learning inference on AWS Greengrass including sample code how to deploy and maintain a custom model for inference trained with Tensorflow!
The sample uses a machine learning resource in AWS IoT Greengrass to deploy required machine learning libraries like Tensorflow for inference on the Greengrass device!

## Who is this for?

This repo is for anyone interested in:

- a maintainable way to deploy your own custom machine learning model for inference on AWS Greengrass
- an example on how to deploy and maintain a Tensorflow model for inference on AWS Greengrass
- an example for a fully automated deployment of AWS Greengrass using AWS CloudFormation and [AWS SAM](https://github.com/awslabs/serverless-application-model)

## Getting started

TODO: Fill in sample execution instructions

## Introduction to ML inference options on AWS Greengrass

With AWS IoT Greengrass, you can [perform machine learning (ML) inference at the edge](https://docs.aws.amazon.com/greengrass/latest/developerguide/ml-inference.html) on locally generated data using cloud-trained models. You benefit from the low latency and cost savings of running local inference, yet still take advantage of cloud computing power for training models and complex processing.

In order to perform ML inference at the edge with [AWS IoT Greengrass](https://aws.amazon.com/greengrass/) you need 3 components deployed on the device:

- the trained machine learning model
- the inference code
- Machine learning libraries required for inference, like Tensorflow, Pytorch or the [Amazon SageMaker Neo deep learning runtime](https://docs.aws.amazon.com/greengrass/latest/developerguide/ml-inference.html#dlc-optimize-info)

Each of these components has different requirements in terms of storage and update frequency:

| Part               | Typical size                 | Update demand frequency                   |
| ------------------ | -----------------------------| ----------------------------------------- |
| 1. ML model        | few MB up to a GB            | medium to high (depending on model decay) |
| 2. Inference logic | usually few KB               | medium                                    |
| 3. ML Libraries    | up to several Gb             | low (new versions, security fixes)        |

Depending on size and and update frequency demand there are several option you can pick for deployment for each of these components.

### Deploying the trained machine learning model

The machine learning model can be included as part of the lambda function deployment package itself or deployed using a ["ML resources"](https://docs.aws.amazon.com/greengrass/latest/developerguide/ml-inference.html) in AWS Greengrass.

Using ML resources is usually the preferred when:

- the model is to big to fit in the maximum deployment package size of a lambda function (50 MB zipped)
- the model should be updated independent of the lambda function code

### Deploying the inference code

The inference code itself is deployed as part of the lambda function. It uses a machine learning library to call the model for inference and returns the results as required within the business context. In a production setting the deployment of the lambda function should be automated ideally using infrastructure as code (IaC). A common tool particularly when automating the deployment of lambda functions is [AWS SAM](https://github.com/awslabs/serverless-application-model).
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

A better option is to bundle required libraries into  ["ML resources"](https://docs.aws.amazon.com/greengrass/latest/developerguide/ml-inference.html) during deployment and load the libraries dynamically
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

## Inspecting the Greengrass ML inference example

TODO: explanation of the sample