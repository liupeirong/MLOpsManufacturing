# Azure Machine Learning Environment

Azure ML supports [**Environment**](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-environments) which you can select configurations to use when running the experiment. There are many out of box Environment configurations, which are called [curated environment](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-environments#use-a-curated-environment).

We usually use one of the existing environments and install dependent python packages by specifiying conda configuration, however, we can also create **Custom Base Image** if existing one doesn't meet our requirements.

## Custom Base Image

Azure ML supports custom docker image as Azure ML Environment. There are three ways to specify custom base imgae for Azure ML pipeline.

- Specify container registory address
- Specify Dockerfile
- Directly embed Dockerfile content

We recommend to build docker image in advance and specify the container registory address. The dokcer image should have all dependencies, softwares and tools, then register it to container registory such as ACR.

[Build custom image](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-custom-docker-image#build-a-custom-base-image) contains sample Dockerfile which describe how to create custom base image.

We add additional requirements into the Dockerfile to create the custom base image.

If you specify Dockerfile or Dockerfile content directly in the Azure ML pipeline build code, the build agent has to build the image everytime the pipeline build, which may take too much time.

## Create Dockerfile

The sample [Dockerfile](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-custom-docker-image#build-a-custom-base-image) contains minimum requirements to run experiment, such as conda environment and Azure ML SDK. We can add dependencies and softwares in the Dockerfile.

### Sample Dockerfile for custom image

This project contains some samples which uses custom base image. See each sample to understand how to write Dockerfile.

[Kaldi yesno sample](../../samples/yesno/environment_setup/azureml_environment/Dockerfile)

## Use custom base image in Azure ML Pipeline

As we explain above, there are three ways to specify custom base image.

### Specify container registory address

This is recommended approach, which you build the image in advance and register to container registory.

If the image is in public repository, you can simply specify the image address.

```python
from azureml.core.environment import Environment
# Create the environment
myenv = Environment(name="myenv")
# Enable Docker and reference an image
myenv.docker.enabled = True
myenv.docker.base_image = "mcr.microsoft.com/azureml/o16n-sample-user-base/ubuntu-miniconda:latest"
```

If the repository requires authentication, then add additional properties.

```python
# Set the container registry information
myenv.docker.base_image_registry.address = "myregistry.azurecr.io"
myenv.docker.base_image_registry.username = "username"
myenv.docker.base_image_registry.password = "password"
```

### Specify Dockerfile

You can also speficy Dockerfile or content directly in Azure ML pipeline building code.

```python
# Specify docker steps as a string. 
dockerfile = r"""
FROM mcr.microsoft.com/azureml/base:intelmpi2018.3-ubuntu16.04
RUN echo "Hello from custom container!"
"""

# Set base image to None, because the image is defined by dockerfile.
myenv.docker.base_image = None
myenv.docker.base_dockerfile = dockerfile

# Alternatively, load the string from a file.
myenv.docker.base_image = None
myenv.docker.base_dockerfile = "./Dockerfile"
```

This is good approach only when:

- You start from image which contains all Azure ML required dependencies
- You only install additional pip packages or do some small changes
