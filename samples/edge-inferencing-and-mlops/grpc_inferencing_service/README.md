# gRPC Inferencing Service <!-- omit in toc -->

This folder contains the gRPC inferencing service.
This service is a container that can be deployed to edge devices for leveraging trained models.

Here is the project outline:

- **client** - folder containing the code for a client that can be run locally hit the service
- **service** - folder containing the code for the service
- **service/core** - folder containing the gRPC server core implementation
- **service/lib** - folder containing the trained model (model is gitignored)
- **service/protos** - folder containing the data contracts (.proto files)
- **service/tests** - folder containing unit tests

## Sections <!-- omit in toc -->

- [Setting Up Your Local Environment](#setting-up-your-local-environment)
- [Download The ML Model](#download-the-ml-model)
- [Running The Server Locally](#running-the-server-locally)
  - [Python Module](#python-module)
  - [Docker](#docker)
    - [Docker-Compose](#docker-compose)
    - [Manually](#manually)
- [gRPC Health Check](#grpc-health-check)
- [Testing](#testing)
- [Interacting With The Server Locally](#interacting-with-the-server-locally)

## Setting Up Your Local Environment

Follow [this documentation](../docs/development/local-env-setup.md) to setup your local environment for Python development.

## Download The ML Model

Before you can run the inferencing service, you will need the ML model. The model can be downloaded from a few places:

1. If trained locally, the model will output in `model/output_model` directory.
   To train locally see [this documentation](../model/README.md).
1. On a successful run of the CI Inferencing Service the model will be located in the `ml-model-files` directory of the published artifacts.
   This will only be possible if you've set up the full project and resources (e.g. AML required).

After downloading the model, name and move the downloaded model file here: `grpc_inferencing_service/service/lib/classifier.pkl`

## Running The Server Locally

- Activate your Python virtual environment
  - If you haven't setup your python environment, [read this first](#setting-up-your-local-environment)
- Set your environment root to be `grpc_inferencing_service/service`
- Run `pip install -r requirements.txt`
- Run `./setup-protos.sh`
  - This copies the relevant proto files and generates the required files.
    These files are git ignored and should not be checked in.
    So each time you want to run the server,
    make sure you have the most up to date files by running the setup script

### Python Module

- Run the server
  - `python -u main.py`

### Docker

You can alternatively run the server using docker.

#### Docker-Compose

Docker-compose enables you to create a YAML file to configure your application’s services, then use a single command to create and start
all the services from your configuration. You can learn more about docker-compose and how to install it [here](https://docs.docker.com/compose/).

- Spin up container: `docker-compose up`
- Spin down container: `docker-compose down`

#### Manually

- `docker build -f Dockerfile -t grpc-inferencing-service:v1 .`
- `docker run -p 50051:50051 grpc-inferencing-service:v1`

## gRPC Health Check

gRPC provides a health check service that we utilize.
You can read about this [here](https://github.com/grpc/grpc/blob/master/doc/health-checking.md).

## Testing

You can run the unit tests using `python -m pytest --without-integration`

You can run integration tests using:

- `export TEST_RESULT_DIRECTORY=./test_results`
- `docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit`
- Make sure to clean up using `docker-compose -f docker-compose.test.yml down`

## Interacting With The Server Locally

You can use our placeholder client to test out your server endpoints and services.

- Make sure the [server is running](#running-the-server-locally)
- Activate your Python virtual environment
- Set your environment root to be `grpc_inferencing_service/client`
- Run `pip install -r requirements.txt`
- Run `./setup-protos.sh`
- Run the client: `python -u main.py`
