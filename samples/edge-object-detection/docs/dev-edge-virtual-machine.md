# Setting up an IoT Edge Virtual Machine for development <!-- omit in toc -->

This document will walk you through how you can setup a linux virtual machine to use as an Edge device for testing and debugging your
IoT Edge modules.

## Sections <!-- omit in toc -->

- [Automated Resource Deployment](#automated-resource-deployment)
- [Deploy the VM resources & Edge runtime](#deploy-the-vm-resources--edge-runtime)
- [Create a Service Principal](#create-a-service-principal)
- [Download the video for the camera simulator](#download-the-video-for-the-camera-simulator)
- [Deploy your IoT Edge modules](#deploy-your-iot-edge-modules)
- [Debugging](#debugging)

## Automated Resource Deployment

This repository has an [automated pipeline](../.pipelines/cd/iac.yml) that deploys all of the resources
needed for edge object detection, including an IoT Edge enabled VM.
However, if you would prefer to just deploy the VM manually, this document explains how to do so.

## Deploy the VM resources & Edge runtime

Follow [this documentation](https://docs.microsoft.com/azure/iot-edge/how-to-install-iot-edge-ubuntuvm#deploy-using-deploy-to-azure-button)
to deploy the virtual machine to Azure. Use the `Deploy to Azure` button for a quick setup.

Alternatively, you can [deploy using the AzCli](https://docs.microsoft.com/azure/iot-edge/how-to-install-iot-edge-ubuntuvm#deploy-from-azure-cli)
if you prefer.

## Create a Service Principal

LVA requires a service principal for the Edge module. You can create one using AzCLI:

1. `az ad sp create-for-rbac --name ServicePrincipalName`
1. Make sure to note down the ID and Secret for this service principal, you will need it in your .env file for IoT Edge module deployments

> [Documentation for creating service principals](https://docs.microsoft.com/cli/azure/create-an-azure-service-principal-azure-cli)

## Download the video for the camera simulator

We will be using `rtspsim` module as our simulated camera source. For this to work you will need to have a video to stream.

1. SSH into your virtual machine `ssh <YOUR_ADMIN_USERNAME>@<DNS_Name>`
1. Make sure there is a `/home/<YOUR_ADMIN_USERNAME>/samples/input/` directory created
1. Switch to the root user `sudo su -`
1. Download the video files:

   `curl https://lvamedia.blob.core.windows.net/public/camera-300s.mkv > /home/<YOUR_ADMIN_USERNAME>/samples/input/truck.mkv`

> NOTE: the video we are uploading here is the video of from the LVA sample. This is a video of a truck passing by on the highway.
> You can change this to a video that you need to simulate for the model you're testing against.
>
> In our DevOps pipelines <YOUR_ADMIN_USERNAME> is usually set to `edgeadmin`. The value for the admin username itself doesn't matter,
> but it does matter where you install the video as these variables all need to match:
>
> - VIDEO_INPUT_FOLDER_ON_DEVICE: '/home/$(edgeVmAdminUsername)/samples/input'
> - VIDEO_OUTPUT_FOLDER_ON_DEVICE: '/home/$(edgeVmAdminUsername)/samples/output'

## Deploy your IoT Edge modules

Follow this documentation on how to
[deploy to an IoT Edge](https://docs.microsoft.com/azure/media-services/live-video-analytics-edge/deploy-iot-edge-device) device.

## Debugging

To debug your modules you need to open the debug port on your virtual machine.

1. [Follow this documentation](https://docs.microsoft.com/azure/virtual-machines/linux/nsg-quickstart) to open ports on your VM
   - You will need to open port `5678`
1. [Follow this documentation](https://docs.microsoft.com/azure/iot-edge/how-to-vs-code-develop-module#debug-a-module-with-the-iot-edge-runtime)
    to debug your module
