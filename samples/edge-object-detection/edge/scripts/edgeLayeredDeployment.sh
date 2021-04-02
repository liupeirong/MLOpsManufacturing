#!/bin/bash
# This script deploys IoT Edge modules using the layered deployment approach

inputs=$@

for ARGUMENT in "$@"
do
    KEY=$(echo $ARGUMENT | cut -f1 -d=)
    VALUE=$(echo $ARGUMENT | cut -f2 -d=)

    case "$KEY" in
            deploymentId)               deploymentId=${VALUE} ;;
            environment)                environment=${VALUE} ;;
            iotHub)                     iotHub=${VALUE} ;;
            deploymentsFolderPath)      deploymentsFolderPath=${VALUE} ;;
            *)
    esac
done

az extension add --name azure-iot

usage(){
  echo "***Azure IoT Edge Layered Deployment Script***"
  echo "Usage: ./edgeLayeredDeployment.sh deploymentId=<deployment.id> environment=<environment> iotHub=<iot.hub> deploymentsFolderPath=<deployment.folder.path>"
  echo "---Parameters--- "
  echo "deploymentId=             :the ID that will be used as part of the name of the edge deployment. Typically the CD pipeline build ID."
  echo "environment=              :the environment of the devices that you want to deploy to. E.g. 'dev' or 'prod'."
  echo "iotHub=                   :the name of the IoT hub."
  echo "deploymentsFolderPath=    :path to the folder that contains the IoT Edge deplotment manifests."
}

handleLayeredDeployments(){
  deleteExistingDeployments
  deployBaseModules
  deployNewLayers
}

deleteExistingDeployments(){
  echo "/////////////////////////////////////////////////////////"
  echo "//                   Delete Stage                      //"
  echo "/////////////////////////////////////////////////////////"

  deployments=($(az iot edge deployment list -n $iotHub --query '[].id' -o tsv))
  if [ ${#deployments[*]} -eq 0 ]
  then
    echo "No deployments found on IoT Hub $iotHub"
  else
    echo "Number of deployments found in $iotHub: ${#deployments[*]}"
    for deployment in ${deployments[*]}
    do
      echo "Deleting deployment: '$deployment'"
      $(az iot edge deployment delete -n $iotHub -d $deployment)
    done
  fi
}

deployBaseModules(){
  echo
  echo "/////////////////////////////////////////////////////////"
  echo "//                   Deploy Stage                      //"
  echo "/////////////////////////////////////////////////////////"

  echo "Starting new deployment using this Id suffix: '$deploymentId'"

  # Deploy base modules
  az iot edge deployment create -d "base-$deploymentId" -n $iotHub --content $deploymentsFolderPath/base.json --target-condition "tags.environment='$environment'"
  # Deploy container insights always
  az iot edge deployment create -d "container-insights-$deploymentId" -n $iotHub --content $deploymentsFolderPath/container.insights.json --target-condition "tags.environment='$environment'" --layered
}

deployNewLayers(){
  echo "Starting layered deployments to $iotHub..."

  jq -c '.[]' $deploymentsFolderPath/layered.config.json | while read i; do
    name=$(echo $i | jq '.deployment' | sed -e 's/^"//' -e 's/"$//')
    path=$(echo $i | jq '.path' | sed -e 's/^"//' -e 's/"$//')
    condition=$(echo $i | jq '.condition' | sed -e 's/^"//' -e 's/"$//')
    az iot edge deployment create -d "$name-$deploymentId" -n $iotHub --content $deploymentsFolderPath/$path --target-condition "tags.environment='$environment' and $condition" --layered
  done
}

# Check Arguments
[[ $inputs < 4 ]] && { usage && exit 1; } || handleLayeredDeployments
