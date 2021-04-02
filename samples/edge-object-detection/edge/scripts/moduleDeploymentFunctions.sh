#!/bin/bash
# This script has functions that are shared across different deployment scripts
# Requires jq and azure cli with iot extension - https://docs.microsoft.com/azure/iot-hub/iot-hub-device-management-iot-extension-azure-cli-2-0

# Validates that a deployment has been applied to a specific device for a specific IoTHub
# Usage
# validateDeploymentHasBeenApplied <deploymentName> <deviceId> <iotHub> <numberOfRetries> <delayInSeconds>
validateDeploymentHasBeenApplied(){
  deploymentName=$1
  deviceId=$2
  iotHub=$3
  numberOfRetries=$4
  delayInSeconds=$5

  deploymentStatus=0
  # Poll until the deployment has been applied or the number of retries is over
  for ((i=1;i<=numberOfRetries;i++));
  do
    if [ $deploymentStatus -eq 0 ]
    then
        deploymentStatus=$(az iot edge deployment show-metric -m appliedCount -d $deploymentName -n $iotHub --mt system --query 'result' -o json | jq '. | length')
        echo "Deployment $deploymentName on device $deviceId state: $deploymentStatus"

        if [ $deploymentStatus -eq 0 ]
        then
          sleep $delayInSeconds
        fi
    else [ $deploymentStatus -ge 1 ]
      echo "Deployment $deploymentName on device $deviceId has been applied."
      break
    fi
  done

  if [ $deploymentStatus -eq 0 ]
  then
    echo "Deployment $deploymentName on device $deviceId has not been applied. Exiting." 1>&2; exit 1;
  fi
}

# Validates that all modules deployed to a device are up and running
# Usage
# validateModulesRunning <deviceId> <iotHub> <numberOfRetries> <delayInSeconds>
validateModulesRunning(){
  deviceId=$1
  iotHub=$2
  numberOfRetries=$3
  delayInSeconds=$4

  echo
  echo "Validating modules are running..."

  # Get all the modules that should be running
  edgeAgentTwin=$(az iot hub module-twin show --module-id '$edgeAgent' --hub-name $iotHub --device-id $deviceId)
  deviceModules=($(echo $edgeAgentTwin | jq -r .properties.desired.modules | jq -r to_entries[].key))
  echo "Number of modules configured for $deviceId: ${#deviceModules[*]}"

  # Loop over all the modules and see if they are running
  for deviceModule in ${deviceModules[*]}
  do
    # Poll the module status until it is running or has failed or we are out of retries
    edgeAgentTwin=$(az iot hub module-twin show --module-id '$edgeAgent' --hub-name $iotHub --device-id $deviceId)
    moduleStatus=$(echo $edgeAgentTwin | jq -r .properties.reported.modules[\"$deviceModule\"].runtimeStatus)
    for ((i=1;i<=numberOfRetries;i++));
    do
      # If the module isn't running, sleep then re-poll
      if [[ $moduleStatus != "running" ]]
      then
        sleep $delayInSeconds
        edgeAgentTwin=$(az iot hub module-twin show --module-id '$edgeAgent' --hub-name $iotHub --device-id $deviceId)
        moduleStatus=$(echo $edgeAgentTwin | jq -r .properties.reported.modules[\"$deviceModule\"].runtimeStatus)
        echo 'device' $deviceId 'module' $deviceModule 'status' $moduleStatus
      else
        echo 'device' $deviceId 'module' $deviceModule 'status' $moduleStatus
        break
      fi
    done
    # See if exited because module was running or because we ran out of retries
    if [[ $moduleStatus != "running" ]]
    then
      echo 'device' $deviceId 'module' $deviceModule 'status' $moduleStatus 'is not running. Exiting.' 1>&2; exit 1;
    fi
  done
}
