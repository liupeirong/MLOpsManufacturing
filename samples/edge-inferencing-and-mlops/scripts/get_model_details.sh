#!/bin/bash

# This script obtains the model details of a Azure ML registered model

inputs=$@

for ARGUMENT in "$@"
do
    KEY=$(echo $ARGUMENT | cut -f1 -d=)
    VALUE=$(echo $ARGUMENT | cut -f2 -d=)

    case "$KEY" in
            modelName)                  modelName=${VALUE} ;;
            resourceGroupName)          resourceGroupName=${VALUE} ;;
            workspaceName)              workspaceName=${VALUE} ;;
            source)                     source=${VALUE} ;;
            buildId)                    buildId=${VALUE} ;;
            label)                      label=${VALUE} ;;
            *)
    esac
done

usage(){
    echo "***Azure ML get model details script***"
    echo "Usage: source get_model_details.sh modelName=<model_name> resourceGroupName=<resource_group_name> workspaceName=<workspace_name> source=<source> buildId=<build_id> label=<label>"
    echo "--- Required Parameters --- "
    echo "<model_name> is the name of the model."
    echo "<resource_group_name> is the name of the resource group of the Azure ML workspace."
    echo "<workspace_name> is the name of the Azure ML workspace."
    echo "<source> is the source from which the model was built."
    echo "--- Optional Parameters --- "
    echo "<build_id> is the build id from which the model was built."
    echo "<label> is the value of the label."
}

getModelDetails(){
  az extension add --name azure-cli-ml --only-show-errors

  echo "Get model details with (modelName=$modelName, resourceGroupName=$resourceGroupName, workspaceName=$workspaceName, source=$source, buildId=$buildId, label=$label)"

  export modelDetails=''

#   properties="--property build_source=$source"

#   if ! [ -z "$buildId" ]
#   then
#     echo "BuildId provided: $buildId"
#     properties="${properties} --property build_id=$buildId"
#   fi

#   if ! [ -z "$label" ]
#   then
#     echo "Label provided: $label"
#     properties="${properties} --tag label=$label"
#   fi

  modelHeaderCommand="az ml model list --model-name $modelName --resource-group $resourceGroupName --workspace-name $workspaceName --latest --query '[0]' -o json"

  echo "Command to retrieve model header: $modelHeaderCommand"

  modelHeader=$(eval $modelHeaderCommand)

  if [ -z "$modelHeader" ]
  then
    echo "Model header not found!"
    return
  fi

  modelId=$(echo $modelHeader | jq -r .id)

  modelDetailsCommand="az ml model show --model-id $modelId --resource-group $resourceGroupName --workspace-name $workspaceName"

  echo "Command to retrieve model details: $modelDetailsCommand"

  export modelDetails=$(eval $modelDetailsCommand)

  if ! [ -z "$modelDetails" ]
  then
    echo "Model details found: $modelDetails"
  else
    echo "Model details not found!"
  fi
}

# Check Arguments
[[ $inputs < 4 ]] && { usage && exit 1; } || getModelDetails
