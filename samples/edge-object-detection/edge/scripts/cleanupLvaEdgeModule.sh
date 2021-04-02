#!/bin/bash

# This script deactivates and deletes the lvaEdge module graph instances for a set of devices

for ARGUMENT in "$@"
do
    KEY=$(echo $ARGUMENT | cut -f1 -d=)
    VALUE=$(echo $ARGUMENT | cut -f2 -d=)

    case "$KEY" in
            moduleId)               moduleId=${VALUE} ;;
            environment)            environment=${VALUE} ;;
            iotHub)                 iotHub=${VALUE} ;;
            *)
    esac
done

az_iot_ext_install_status=$(az extension show --name azure-iot)
az_iot_ext_install_status_len=${#az_iot_ext_install_status}

if [ $az_iot_ext_install_status_len -eq 0 ]
then
    az extension add --name azure-iot
fi

# Get list of all devices where tag.lva = true for a given environment
query="[?tags.environment=='$environment'&&tags.lva=='true'].deviceId"
deviceList=$(az iot hub device-identity list -n $iotHub --query $query)

# Loop through every device (using sed to remove double qoutes)
# Go through instance list to deactivate and delete any graph instance found
for device in $(echo "${deviceList}" | jq '.[]' | sed -e 's/^"//' -e 's/"$//'); do
    instanceList=$(az iot hub invoke-module-method -d $device --mn 'GraphInstanceList' -m $moduleId -n $iotHub --method-payload "{ '@apiVersion': '2.0' }" | jq -r '.payload.value')

    if [ -z "$instanceList" ]; then
        echo "lvaEdge module is not available on device $device"
        break
    fi

    doesHaveInstance=$(echo "${instanceList}" | jq -r 'has(0)')

    if $doesHaveInstance; then
        echo "Graph instances found on device $device."

        for instance in $(echo "${instanceList}" | jq -r '.[] | @base64'); do
            _jq() {
                echo ${instance} | base64 --decode | jq -r ${1}
            }

            name=$(_jq '.name')
            state=$(_jq '.properties.state')

            if [ "$state" = "Active" ]; then
                echo "Graph instance $name is active. Now deactivating . . ."
                az iot hub invoke-module-method -d $device --mn 'GraphInstanceDeactivate' \
                    -m 'lvaEdge' -n $iotHub --method-payload "{ '@apiVersion': '2.0', 'name': '$name' }"
            else
                echo "Graph instance $name is inactive."
            fi

            echo "Deleting graph instance $name . . ."
            az iot hub invoke-module-method -d $device --mn 'GraphInstanceDelete' \
                    -m 'lvaEdge' -n $iotHub --method-payload "{ '@apiVersion': '2.0', 'name': '$name' }"
        done
    else
        echo "Graph instances not found on device $device."
    fi
done
