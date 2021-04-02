# Architecture <!-- omit in toc -->

This design document illustrates the architecture of the object detection on the edge sample project.

## Sections <!-- omit in toc -->

- [Overview](#overview)
- [Resources](#resources)
- [Architecture](#architecture)

## Overview

The goal of the this sample project is to demonstrate how you can detect objects on the edge. At a high level, we want to capture video
from a device running on the edge, send video frames to a machine learning model, and then to act on the results. The idea is for this
IoT pipeline to be generic where possible so that we can use this solution to trial various different video based ML models on the edge.
Things that are expected to change are:

- The business logic module running on the device
- The AI inferencing module running on the device
- The configuration for capturing video through LVA

## Resources

The following are the Azure resources for the sample project:

| Resource | SKU      | Description |
| -------  | -------  | ---------   |
| Container Registry    | Standard                  | For managing Edge module docker containers |
| Key Vault             | Standard                  | For managing resource secrets and certificates |
| Azure Monitor         | Included with resources   | For monitoring Edge devices and module telemetry |
| IoT Hub               | S1                        | For management of Edge devices, modules, and messages |
| Media Services        | S2                        | For capturing and management of video streams |
| Azure Storage (Block Blob)| Standard (GPv2) storage - Hot - LRS* | For storage of captured video streams |

> \* LRS is fine for our PoC, but RA-GRS is recommended for production.

## Architecture

![iot architecture](/docs/images/arch-diagram.png)

1. We capture video from cameras using RTSP. This is done through the LVA Edge module which has a built-in RTSP source.

1. LVA sends captured video frames to the AI inferencing service using the gRPC extension component.

1. The inferencing service analyzes the frames and determines if an object has been detected. Results are sent back to LVA and sent as
   a message to the IoT Edge Hub (on device), using the IoT Hub message sink in the LVA module.

1. The business logic listens to messages on the Edge Hub for messages from LVA indicating an object has been detected. The business logic
   analyses the results to determine an action and sends as a message to the Edge Hub and upstream to the IoT Hub in Azure.

1. When the business logic determines this is an event we care about, the signal gate in LVA opens and we use the asset sink in the LVA
   module to send raw video of the event to Azure Media Service.

1. Azure Media Services stores assets in Azure Storage V2.

1. The IoT Hub manages the Edge device, and the modules deployed to it. The IoT Hub also manages the messages captured from the Edge
device modules.

1. The telemetry and logs captured by the IoT Hub (built-in) can be viewed and managed using Azure Monitor. A dashboard can be created
to view all IoT Edge device operation metrics. Azure Monitor can store the data in Blob storage if required for archive.

1. Azure KeyVault will be used to manage all credentials. certificates, and secrets of resources. It will be consumed by Azure DevOps
for the CI/CD process. It will be consumed by Azure IoT Hub to manage device certificates.

1. IoT Edge modules will be developed and deployed using Azure DevOps. The CI/CD pipelines will build and publish new containers to
Azure Container Registry. The IoT Hub uses connects to the registry to grab modules and deploy them to the Edge device.
