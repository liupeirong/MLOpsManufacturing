#!/bin/bash
# IoT Edge Smoke Test Script
# Requires jq and azure cli with iot extension - https://docs.microsoft.com/azure/iot-hub/iot-hub-device-management-iot-extension-azure-cli-2-0

source $(pwd)/moduleDeploymentFunctions.sh

inputs=$@

for ARGUMENT in "$@"
do
    KEY=$(echo $ARGUMENT | cut -f1 -d=)
    VALUE=$(echo $ARGUMENT | cut -f2 -d=)

    case "$KEY" in
            h)               h=${VALUE} ;;
            v)               v=${VALUE} ;;
            d)               d=${VALUE} ;;
            r)               r=${VALUE} ;;
            s)               s=${VALUE} ;;
            t)               t=${VALUE} ;;
            i)               i=${VALUE} ;;
            *)
    esac
done

deploymentId=${i:=None}
iothub_name=${h:=None}
device_tag_value=${v:=None}
delayInSeconds=${d:=6}
numberOfRetries=${r:=60}
singleDeviceTest=${s:="false"}
device_tag=${t:="environment"}

usage(){
    echo "***Azure IoT Edge Smoke Test Script***"
    echo "Usage: ./edgeSmokeTest.sh h=<iothub_name> v=<device_tag_value> i=<iot_deployment_id>"
    echo "---Parameters--- "
    echo "<iothub_name> is the name of your IoT Hub."
    echo "<device_tag_value> is the value of the device_tag to determine which devices to target."
    echo "<iot_deployment_id> is the suffix value of the deployment name i.e. for the deployment 'base-1234', 1234 would be the Id."
    echo "---Optional Parameters--- "
    echo "d=    :delay in seconds until re-poll module twin. Default is 6 seconds"
    echo "r=    :number of retries. Default is 60"
    echo "s=    :using this switch enables single device test otherwise defaults to test all devices matching the value of the device_tag. Pass the single deviceId to <device_tag_value> with this switch enabled."
    echo "t=    :device_tag used to query for which IoT Edge devices to find.  If not specified, a tag called environment will be used."
}

startTest(){
  az_iot_ext_install_status=$(az extension show --name azure-iot)
  az_iot_ext_install_status_len=${#az_iot_ext_install_status}

  if [ $az_iot_ext_install_status_len -eq 0 ]
  then
      az extension add --name azure-iot
  fi

  if [[ $singleDeviceTest != "false" ]]
  then
    devices=($device_tag_value)
    echo "Testing a single device with deviceId $device_tag_value"
    deviceExists=$(az iot hub device-identity show -n $iothub_name -d $device_tag_value)
    if [ ! $? == 0 ]; then
      echo "An IoT Edge device twin with deviceId $device_tag_value cannot be found."
      exit 1
    fi
    device_tag="deviceId"
  else
    devices=($(az iot hub query --hub-name $iothub_name --query-command "SELECT * FROM devices WHERE tags.$device_tag = '$device_tag_value'" --query '[].deviceId' -o tsv))
    if [ ${#devices[*]} -eq 0 ]
    then
            echo "No devices with tag $device_tag of value $device_tag_value found in $iothub_name"
            return 1
    else
            echo "Number of devices with tag $device_tag of value $device_tag_value found in $iothub_name: ${#devices[*]}"
    fi
  fi

  validateDevicesConnectedToIoTHub

  # Check the core deployments have been applied
  echo
  echo "Validating deloyments where $device_tag = $device_tag_value are currently applied to the iot hub..."
  # This function is defined in the moduleDeploymentFunctions.sh file sourced
  validateDeploymentHasBeenApplied "base-$deploymentId" "$device" "$iothub_name" $numberOfRetries $delayInSeconds
  validateDeploymentHasBeenApplied "container-insights-$deploymentId" "$device" "$iothub_name" $numberOfRetries $delayInSeconds
  validateDeploymentHasBeenApplied "lva-$deploymentId" "$device" "$iothub_name" $numberOfRetries $delayInSeconds
  validateDeploymentHasBeenApplied "business-logic-$deploymentId" "$device" "$iothub_name" $numberOfRetries $delayInSeconds

  # This is needed because old modules aren't stopped when a deployment is deleted,
  # rather they are stopped when new deployments are created
  # Because of this we need to wait until new deployments are applied for the old modules to stop
  # and sometimes when we validate that the modules are running, we actually see old modules
  # running that haven't stopped yet (and think it's the new ones up and running)
  sleep 30

  validateDevicesModulesRunning
  validateLvaRunning
}

validateDevicesConnectedToIoTHub(){
  echo
  echo "Validating devices where $device_tag = $device_tag_value are currently connected to the iot hub..."
  for device in ${devices[*]}
  do
    pingStatus=unknown
    for ((i=1;i<=numberOfRetries;i++));
    do
      if [[ $pingStatus != "200" ]]
      then
        pingStatus=($(az iot hub invoke-module-method --method-name 'ping' --module-id '$edgeAgent' --hub-name $iothub_name --device-id $device --query 'status' -o tsv))
        echo 'device' $device 'ping status: ' $pingStatus
        sleep $delayInSeconds
      fi
    done
    if [[ $pingStatus != "200" ]]
    then
      echo $device 'is not connected with ping status' $pingStatus 'exiting.' 1>&2; exit 1;
    fi
  done
}

validateDevicesModulesRunning(){
  echo
  echo "Validating devices where $device_tag = $device_tag_value configured modules are running..."
  # Check that all the modules are running on all the devices
  for device in ${devices[*]}
  do
    # This function is defined in the moduleDeploymentFunctions.sh file sourced
    validateModulesRunning "$device" "$iothub_name" $numberOfRetries $delayInSeconds
  done
}

validateLvaRunning(){
  echo
  echo "Validating lvaEdge module running for devices where $device_tag = $device_tag_value ..."
  # Check that all the modules are running on all the devices
  for device in ${devices[*]}
  do
    # Poll the module status until it is running or has failed or we are out of retries
    lvaModuleTwin=$(az iot hub module-twin show --module-id 'lvaEdge' --hub-name $iothub_name --device-id $device)
    moduleStatus=$(echo $lvaModuleTwin | jq -r .properties.reported.State)
    for ((i=1;i<=numberOfRetries;i++));
    do
      # If the module isn't running, sleep then re-poll
      if [[ $moduleStatus != "Running" ]]
      then
        sleep $delayInSeconds
        lvaModuleTwin=$(az iot hub module-twin show --module-id 'lvaEdge' --hub-name $iothub_name --device-id $device)
        moduleStatus=$(echo $lvaModuleTwin | jq -r .properties.reported.State)
        echo 'device:' $device 'lvaEdge module status:' $moduleStatus
      else
        echo 'device:' $device 'lvaEdge module status:' $moduleStatus
        break
      fi
    done
    # See if exited because module was running or because we ran out of retries
    if [[ $moduleStatus != "Running" ]]
    then
      echo 'device:' $device 'lvaEdge module status:' $moduleStatus '. Exiting.' 1>&2; exit 1;
    fi
  done
}

# Check Arguments
[[ $inputs < 3 ]] && { usage && exit 1; } || startTest
