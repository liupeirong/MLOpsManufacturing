# Azure IoT Edge Project <!-- omit in toc -->

This project is for the development of IoT Edge modules.

- [Start Here](#start-here)
- [Folder Contents](#folder-contents)
- [Deployment Manifest Templates](#deployment-manifest-templates)
- [Setup](#setup)
  - [Environment Variables](#environment-variables)
  - [Generate manifest](#generate-manifest)
  - [Deploy](#deploy)
  - [Debug](#debug)
- [Log Level](#log-level)
- [Troubleshooting the LVA Edge Module](#troubleshooting-the-lva-edge-module)

## Start Here

For anyone new to IoT Edge, it is recommended you [follow this tutorial](https://docs.microsoft.com/azure/iot-edge/tutorial-develop-for-linux)
first to get everything setup, and to gain a better understanding of how IoT Edge works.

## Folder Contents

Here is a general guide of the project's folder structure for reference.

- [.vscode](/.vscode) | Folder containing launch settings for running the project in VSCode
- [modules](/modules) | Folder containing all Edge module code
  - individual module | Each module should have its own folder containing
    - `requirements.txt`
    - `module.json`
    - `Dockerfile`
    - `main.py`
- [tests](/tests) - folder for Edge module unit and integration tests
  - filename guidance `test_<moduleName>`

## Deployment Manifest Templates

Deployment manifest templates contain the information about which modules should be deployed into an IoT Edge device, and their configurations.
Only one manifest can be deployed on a device at any one time. Deploying a manifest will overwrite any other modules running on the device.

## Setup

### Environment Variables

Create a `.env` file containing:

```txt
SUBSCRIPTION_ID="<azure_subscription_id>"
AAD_TENANT_ID="<tenant_id>"
AAD_SERVICE_PRINCIPAL_ID="<service_principal_id>"
AAD_SERVICE_PRINCIPAL_SECRET="<service_principal_secret>"

RESOURCE_GROUP="<resource_group>"
AMS_ACCOUNT="<media_service_account>"
APPINSIGHTS_INSTRUMENTATIONKEY="<app insights instrumentation key>"

ACR_USER="<acr_username>"
ACR_PASSWORD="<acr_password>"
ACR_ADDRESS="<acr_username>.azurecr.io"
IMAGE_TAG="<docker_image_tag>"

# Container insights settings (follow documentation here for initial setup: https://labs.iotedge.dev/codelabs/edgemon-preview/#0)
IOT_HUB_RESOURCE_ID="/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/providers/Microsoft.Devices/IotHubs/<IOTHUB_NAME>"
LOG_ANALYTICS_WORKSPACE_ID="<Log Analytics Workspace ID>"
LOG_ANALYTICS_WORKSPACE_KEY="<Log Analytics Workspace key>"
CONTAINER_INSIGHTS_ENDPOINTS="http://edgeHub:9600/metrics,http://edgeAgent:9600/metrics,http://lvaEdge:9600/metric"

VIDEO_INPUT_FOLDER_ON_DEVICE="/home/<YOUR_ADMIN_USERNAME>/samples/input"
VIDEO_OUTPUT_FOLDER_ON_DEVICE="/home/<YOUR_ADMIN_USERNAME>/samples/output"
```

> In our DevOps pipelines <YOUR_ADMIN_USERNAME> is usually set to `edgeadmin`

### Generate manifest

To generate a deployment manifest from the template, right click on the template file and select `Generate IoT Edge deployment manifest`.
This will create the corresponding deployment manifest file in `./config` folder.

> Make sure you have the Azure IoT Tools extension installed

### Deploy

Once you have the manifest in the `./config` folder, right click on the manifest file and select `Create Deployment for Single Device`.

### Debug

- Open this project using VSCode, specifically from the `edge/` folder

- Make sure port `5678` is open on your edge device

- Add this to the import section of the edge module `main.py` file

  ```python
  import ptvsd
  ptvsd.enable_attach(('0.0.0.0',  5678))
  ```

- Replace `0.0.0.0` with the public IP address of the edge device

- Add `breakpoint()` to the function you want to break on when debugging, for example

  ```python
  async def message_handler(message):
    breakpoint() # I am adding a breakpoint here
    if message.input_name == "detectedObjects":
        logging.debug("Message received on detectedObjects route")
  ```

- In the `.vscode/launch.json` file in this folder, update the `host` value with the public IP address of the edge device

- Right-click on the `deployment.debug.template.json` and select `Build and Push IoT Edge solution`

- In the `config/` folder, right-click on the `deployment.debug.amd64.json` file and select `Create Deployment for a Single Device`,
  then select your edge device

- Navigate to the debug tab in VS Code and run the debugger `ObjectDetectionBusinessLogic Module Remote Debug (Python)`

## Log Level

You can set the log level of the business logic module using the `logLevel` module property.

```json
  "objectDetectionBusinessLogic": {
    "properties.desired": {
      "logLevel": "INFO"
    }
  }
```

Accepted values:

- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`
- `CRITICAL`

## Troubleshooting the LVA Edge Module

There is a great troubleshooting guide provided by the LVA product team, you can read the documentation [here](https://docs.microsoft.com/azure/media-services/live-video-analytics-edge/troubleshoot-how-to).

One thing you might want to consider is adding `MediaPipeline` log category in the deployment manifest, you can update the `logCategories`
property under the lvaEdge desired properties section of the manifest. This log category is already enabled as part of our debug deployment
manifest. Read more about LVA logging [here](
https://docs.microsoft.com/azure/media-services/live-video-analytics-edge/monitoring-logging#logging).

> MediaPipeline: Low-level logs that might offer insight when you're troubleshooting problems, like difficulties establishing a
> connection with an RTSP-capable camera.
