# LVA Console App <!-- omit in toc -->

This directory contains a python console application that would enable you to invoke LVA on IoT Edge Direct Methods in a sequence and with
parameters, defined by you in a JSON file (operations.json).

## Sections <!-- omit in toc -->

- [Folder Contents](#folder-contents)
- [Setup](#setup)
  - [DEVICE_ID vs DEVICE_TAG](#device_id-vs-device_tag)
  - [Running](#running)
- [Operation Files](#operation-files)
- [Topology Files](#topology-files)

## Folder Contents

Here is a general guide of the folder structure for reference.

- `main.py` - The main program file
- `requirements.txt` - List of all dependent Python libraries
- `operations/` - JSON files defining the sequence of operations to execute upon
- `topologies/` - JSON files defining what nodes are used in the media graph, and how they are connected within the media graph

## Setup

Create a file named `.env` in this folder. Add the following text and provide values for all parameters.

```txt
IOTHUB_CONNECTION_STRING=
DEVICE_ID=
DEVICE_TAG= // OPTIONAL
TAG_VALUE= // OPTIONAL
MODULE_ID=
OPERATIONS_FILENAME=
```

- **IoTHubConnectionString** - Refers to the connection string of your IoT hub. This should have registry write and service connect access.
- **deviceId** - Refers to the IoT Edge device ID (registered with your IoT hub)
- **deviceTag** - Refers to the tag we want to filter for your IoT Edge device ID (registered with your IoT hub)
- **tagValue** - Refers to the value of the deviceTag
- **moduleId** - Refers to the module ID of LVA on IoT Edge module (when deployed to the IoT Edge device).
- **operationsFilename** - The name of the operations file the console app should load in.

### DEVICE_ID vs DEVICE_TAG

You do not need both the `DEVICE_ID` and the `DEVICE_TAG` environment variables, just one or the other.

For a single device operation, provide the `DEVICE_ID`. This will call the method operations against one device and does not use tags.

For multiple devices (also works with a single device), provide the `DEVICE_TAG` and `TAG_VALUE`. This approach will fetch a list of all
devices registered in your IoT Hub that match the criteria of the given the tag and its value. This is the approach used by our CD pipeline
to activate LVA on multiple devices at the same time.

> If using `DEVICE_TAG`, you **must** also provide `TAG_VALUE`

### Running

- `pip install -r requirements`
- `py main.py`

## Operation Files

The operation json files are a set of parameters that we feed into the console app in order to call direct methods on the IoT Hub.
Essentially, this file is defining the "functions" we want to call on the LVA Edge module, through IoT Hub.

- **operations_local** - This file sets, activates and deactivates the graph instances. Use this version of the operations file locally.
- **operations_setup** - This file *only* sets and activates the topologies, this is made for our CD pipeline and use in production as
  we want our graph to be long running, and not torn down immediately (like in the `_local` file).
- **operations_teardown** - This file **only** deactivates and deletes the topologies and graph instances running on the device. This is
  also for a CD pipeline in case we ever need to replace an existing instance currently running.

## Topology Files

The topology json files represent the media graph architecture we want to deploy for the LVA module running on the Edge device. You can
read more about the topology design in [this design document](/docs/design-lva-topology).
