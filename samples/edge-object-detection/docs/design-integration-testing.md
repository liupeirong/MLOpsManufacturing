# Integration Testing <!-- omit in toc -->

## Sections <!-- omit in toc -->

- [Integration Testing Goals](#integration-testing-goals)
  - [Our Setup](#our-setup)
    - [Deploying Resources](#deploying-resources)
    - [Deploy Modules Script](#deploy-modules-script)
    - [Issues](#issues)
  - [Writing New Tests](#writing-new-tests)
- [Alternative Options](#alternative-options)

## Integration Testing Goals

The goals of integration testing, is to make sure that a core component is acting as it should, at a higher level than unit testing.

So for example, for our business logic module, we can unit test all of it's function individually,
but if we want to test that it is listening to the right IoT Edge inputs, and properly going through it's motions,
we would want more an end to end integration test.
An example integration test would be, deploy the module, send a message out to IoTHub that the business logic should react to,
and validate that the business logic sends the correct output.
That is something that can be validated in an integration test but not a unit test.
And it is something that is important to validate because other components are relying on it behaving the way it says it does.

The next few sections will explain how we are doing exactly that.

### Our Setup

Unfortunately, in order to run integration testing of IoT Edge modules,
there is no good way to do that without actually deploying the modules to a device with IoT Edge installed and go through a real IoT Hub.
This is because the edge modules rely heavily on the edgeAgent and edgeHub modules to route messages into and out of the modules.

Because of this, in order to run integration testing, we need to deploy the module we want to test to a device (VM to be more precise)
that is connected to an IoT Hub. We also need to create a mock module that is used to send the message we want on the proper route.
The reason for this is if we send a device to cloud message directly from the [Azure python iot sdk](https://github.com/Azure/azure-iot-sdk-python)
it skips the edgeHub. The edgeHub is used for routing messages from one module to another.
So the only way to actually send a message from one module to another through the edgeHub, is to deploy a mock module.
That mock module can be very simple in it's code,
as it's sole purpose is to send a desired message to the edgeHub to trigger the other module.

For example: our business logic module listens to edgeHub messages from `lvaEdge/outputs/detectedObjects`
so we created an lvaMock module that sends whatever output message we want to that route.
That way we are in control of what messages the business logic sees, and we can test that it accurately acts accordingly.
The mock module is invoked via a direct method, which you can send using the [Azure python iot sdk](https://github.com/Azure/azure-iot-sdk-python).
That direct method just passes through whatever it iis sent to the output, and voila, you are ready to test different scenarios.

For a whole host of reasons, you don't want to run integration tests (on potentially broken code) on actual production devices or IoT Hubs.
For concurrency purposes you also don't want to share an IoT Hub for everything to run integration tests on.
Imagine a scenario where two pipelines each want to run integration tests on the same IoT Hub at the same time,
things will get very complicated very fast.

Because of everything above, each time we want to run an integration test, we spin up a sandboxed environment specific to that build,
deploy a new IoT Hub and IoT Edge device, deploy the modules we want to test, run the integration tests, then delete the sandboxed environment.
Below will explain how we are doing this

#### Deploying Resources

All of the resources needed for integration testing are deployed as steps in the [iot-integration-test template file](../.pipelines/templates/iot-integration-test.yml).

The resource creation steps in this file are:

1. Creates a new resource group
1. Deploys an IoT Hub to that resource group
1. Creates an edge device in the IoT Hub
1. Deploys a VM that has IoT Edge installed to the resource group
   - Between this and the next step we deploy the modules we want to test, and run the integration tests
1. Deletes the resource group and everything in it

#### Deploy Modules Script

Once we have the resources set up, we must then deploy the edgeAgent and edgeHub modules, as well as whatever modules we want to test.
This is done using the [integrationTestLayeredDeployment.sh script](../edge/scripts/integrationTestLayeredDeployment.sh).
There is documentation within the script about what parameters the script takes in.

At a high level, what the script does is:

1. Deploy edgeAgent and edgeHub modules
1. Deploy the module you want to integration test
   - For us for now that is the objectDetectionBusinessLogic module
1. Deploy any mock modules needed to integration test
   - For us this means deploying an LVA mock module so that we can trigger the business logic
1. Validates that all deployments were applied to the device
1. Validates that all modules are up and running

Once all these steps are met, you are ready to run your integration test file!

#### Issues

You cannot use the iot hub sdk device to cloud messages to trigger routes.
This is because the device to cloud message from the SDK doesn't go through the edge hub,
so it never gets routed into the brokeredEndpoint needed to trigger the correct modules.
This is why we needed to use the mockModules mentioned above.

### Writing New Tests

We've created a test handler [edgeModuleTestHandler.py](../edge/tests/edgeModuleTestHandler.py)
which takes care of managing the concurrency of listening to messages coming into the event hub
and sending messages to whatever module you want to send them to.
This class will loop until it has been too long for the event hub to go without receiving a message,
at that point the test handler will stop the test.

It is the responsibility of the test file itself to know whether the test has failed or passed,
the test handler just handles running the loop and routing the proper messages.

In order to write a new test, look at what is being done in [test_objectDetectionBusinessLogic_highConfidence.py](../edge/tests/integration-tests/test_objectDetectionBusinessLogic_highConfidence.py).
The connection strings and device name we are sending our test to are passed in as arguments for the test.
A message handling function is passed into the testHandler.
This message handling function is where all the event hub messages will be routed,
and the test case can then analyze to see if it got what it expected or not.
Then the global bool of test_passed can be set to true or false and when the test is over that will be reported.

For example, another integration test that would be easy to write, is one where we don't expect a message from the business logic,
something like test_objectDetectionBusinessLogic_lowConfidence.py For this we would expect the threshold to be too low to trigger an alert.
One way to test this would be to set the initial test_passed to True,
and if we get any messages to the message handling function, we can set the test pass to false because we are expecting none.

Or another example is to check timeout integration testing.
With this we might expect one message to come but not a second one.

## Alternative Options

Instead of deploying a real IoT Hub and real modules to IoT Edge to integration test them,
it would be nice to be able to test them by just doing a docker run of the container we want to test and simulate the edgeHub and edgeAgent.
This would make all the required resource setup above obsolete and integration testing would be faster and more simple,
as you could treat every module just as the docker container it is, instead of an edge module relying on the actual IoT Edge to be running.
There is a tool that _MIGHT_ be able to do that and it's called [IoT EdgeHubDev](https://github.com/Azure/iotedgehubdev).
We didn't have time to evaluate that option,
but it seems to be a viable option to simulate the IoT Edge needing far less actual resources up.
It is something to potentially examine in the future.
