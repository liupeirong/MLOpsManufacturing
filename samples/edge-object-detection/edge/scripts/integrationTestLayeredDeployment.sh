#!/bin/bash
# This script deploys IoT Edge modules using the layered deployment approach

source $(pwd)/moduleDeploymentFunctions.sh

inputs=$@

for ARGUMENT in "$@"
do
    KEY=$(echo $ARGUMENT | cut -f1 -d=)
    VALUE=$(echo $ARGUMENT | cut -f2 -d=)

    case "$KEY" in
            deploymentId)               deploymentId=${VALUE} ;;
            environment)                environment=${VALUE} ;;
            deviceId)                   deviceId=${VALUE} ;;
            iotHub)                     iotHub=${VALUE} ;;
            deploymentsFolderPath)      deploymentsFolderPath=${VALUE} ;;
            d)                          d=${VALUE} ;;
            r)                          r=${VALUE} ;;
            *)
    esac
done

delayInSeconds=${d:=6}
numberOfRetries=${r:=60}

# Piping to std error to dev null because it prints error if extension is already installed
az extension add --name azure-iot 2>/dev/null

usage(){
  echo "***Azure IoT Edge Layered Deployment Script***"
  echo "Usage: ./edgeLayeredDeployment.sh deploymentId=<deployment.id> environment=<environment> deviceId=<deviceId> iotHub=<iot.hub> deploymentsFolderPath=<deployment.folder.path>"
  echo "---Parameters--- "
  echo "deploymentId=             :the ID that will be used as part of the name of the edge deployment. Typically the CD pipeline build ID."
  echo "environment=              :the environment of the devices that you want to deploy to. E.g. 'dev' or 'prod'."
  echo "deviceId=                 :the deviceId in the IoTHub for the device."
  echo "iotHub=                   :the name of the IoT hub."
  echo "deploymentsFolderPath=    :path to the folder that contains the IoT Edge deplotment manifests."
  echo "---Optional Parameters--- "
  echo "d=                        :delay in seconds until re-poll module twin. Default is 6 seconds"
  echo "r=                        :number of retries. Default is 60"
}

handleLayeredDeployment(){
  deployBaseModules
  deployBusinessLogicTestingModules

  # These functions are defined in the moduleDeploymentFunctions.sh file sourced
  validateDeploymentHasBeenApplied "base-$deploymentId" "$deviceId" "$iotHub" $numberOfRetries $delayInSeconds
  validateDeploymentHasBeenApplied "business-logic-$deploymentId" "$deviceId" "$iotHub" $numberOfRetries $delayInSeconds
  validateDeploymentHasBeenApplied "lva-mock-$deploymentId" "$deviceId" "$iotHub" $numberOfRetries $delayInSeconds
  validateModulesRunning "$deviceId" "$iotHub" $numberOfRetries $delayInSeconds
}

deployBaseModules(){
  echo
  echo "/////////////////////////////////////////////////////////"
  echo "//               Deploy Base Module                    //"
  echo "/////////////////////////////////////////////////////////"

  echo "Starting new deployment using this Id suffix: '$deploymentId'"

  # Deploy base modules
  az iot edge deployment create -d "base-$deploymentId" -n $iotHub --content $deploymentsFolderPath/base.json --target-condition "tags.environment='$environment'"
}

deployBusinessLogicTestingModules(){
  echo
  echo "/////////////////////////////////////////////////////////"
  echo "//    Deploy Business Logic and LVA Mock Module        //"
  echo "/////////////////////////////////////////////////////////"

  echo "Starting layered deployment of busines logic module to $iotHub"
  az iot edge deployment create -d "business-logic-$deploymentId" -n $iotHub --content $deploymentsFolderPath/business-logic/object.detection.json --target-condition "tags.environment='$environment'" --layered
  echo "Starting layered deployment of lva mock module to $iotHub"
  az iot edge deployment create -d "lva-mock-$deploymentId" -n $iotHub --content $deploymentsFolderPath/mocks/lva.mock.json --target-condition "tags.environment='$environment'" --layered
}

# Check Arguments
[[ $inputs < 5 ]] && { usage && exit 1; } || handleLayeredDeployment
