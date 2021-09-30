#!/bin/bash

opts_count=0
while getopts n:r:w:s:i:c:d:l:f: flag
do
    case "${flag}" in
        n)                            modelName=${OPTARG}; ((opts_count=opts_count+1)) ;;
        r)                        resourceGroup=${OPTARG}; ((opts_count=opts_count+1)) ;;
        w)                            workspace=${OPTARG}; ((opts_count=opts_count+1)) ;;
        s)                          buildSource=${OPTARG}; ((opts_count=opts_count+1)) ;;
        i)                      pipelineBuildId=${OPTARG}; ((opts_count=opts_count+1)) ;;
        c)                     calibrationError=${OPTARG}; ((opts_count=opts_count+1)) ;;
        d)                      devSetpointRmse=${OPTARG}; ((opts_count=opts_count+1)) ;;
        l)                           modelLabel=${OPTARG}; ((opts_count=opts_count+1)) ;;
        f)                           configFile=${OPTARG}; ((opts_count=opts_count+1)) ;;
        *)                                     echo "Unknown parameter passed"; exit 1 ;;
    esac
done

usage(){
    echo "**Model Comparison Script***"
    echo "Set the following environment variables before running this script:"
    echo "    SERVICE_PRINCIPAL_ID, SERVICE_PRINCIPAL_SECRET, TENANT_ID"
    echo "Usage: ./model_comparison.sh -n recommendation -r rg-mlstuff -w myWorkspace -s local -i 653 -c calibration_err_rmse -d dev_setpoint_rmse -l best_sl_recommendation -f config/config.json"
    echo "---Parameters---"
    echo "n=    :model name"
    echo "r=    :azure ml workspace resource group name"
    echo "w=    :workspace name"
    echo "s=    :build source"
    echo "i=    :pipeline build id"
    echo "c=    :calibration error model rmse"
    echo "d=    :dev setpoint rmse"
    echo "l=    :model label"
    echo "f=    :model config file e.g. config/config.json"
}

login () {
  echo "Login using service principal $SERVICE_PRINCIPAL_ID"
  az login --service-principal -u $SERVICE_PRINCIPAL_ID -p=$SERVICE_PRINCIPAL_SECRET --tenant $TENANT_ID

  if [ $? -eq 0 ]; then
      echo "Login successful"
  else
      echo "Login failed. Exiting..."
      exit 1
  fi
}

compareModels () {
  local rg=$1
  local workspace=$2
  local currentCalibrationErrorRmse=$3
  local currentDevSetpointRmse=$4
  local existingCalibrationErrorRmse=$5
  local existingDevSetpointRmse=$6
  local existingModelId=$7

  if [[ $existingCalibrationErrorRmse < $currentCalibrationErrorRmse || $existingDevSetpointRmse < $currentDevSetpointRmse ]]
  then
    echo "Current model has a higher rmse than existing model. Will not update best model label."
    exit
  else
    echo "Current model is the same or better than the existing model. Will remove best model label from existing model."
    az ml model update \
      --model-id $existingModelId \
      --remove-tag 'label' \
      --resource-group $rg \
      --workspace-name $workspace

    if [ $? -eq 0 ]; then
        printf "\nSuccessfully removed best model label from existing model."
    else
        printf "\nSomething went wrong when trying to remove the label. Exiting to avoid duplicates..."
        exit 1
    fi
  fi
}

start () {
  login

  # Creates labelName variable using config name
  labelName=$(bash prepare_model_label.sh -l $modelLabel -f $configFile)

  printf "\nGet current model using build Id\n"
  source get_model_details.sh \
          modelName=$modelName \
          resourceGroupName=$resourceGroup \
          workspaceName=$workspace \
          source=$buildSource \
          buildId=$pipelineBuildId

  # Unset variables in get_model_details so that we can reuse the script without the build_id property being set
  echo "Unsetting buildId script variable..."
  unset buildId

  currentModelDetails=$modelDetails
  currentModelId=$(echo $currentModelDetails | jq -r .id)
  currentCalibrationErrorRmse=$(echo $currentModelDetails | jq -r .properties.$calibrationError)
  currentDevSetpointRmse=$(echo $currentModelDetails | jq -r .properties.$devSetpointRmse)

  echo "Current Calibration Error model rmse: $currentCalibrationErrorRmse"
  echo "Current Dev Setpoint model rmse: $currentDevSetpointRmse"

  if [ -z "$currentModelDetails" ]
  then
    printf "\nCurrent model not found!"
    exit 1
  fi

  printf "\nGet existing model using label\n"
  source get_model_details.sh \
          modelName=$modelName \
          resourceGroupName=$resourceGroup \
          workspaceName=$workspace \
          source=$buildSource \
          label=$labelName

  existingModelDetails=$modelDetails
  existingModelId=$(echo $existingModelDetails | jq -r .id)
  existingCalibrationErrorRmse=$(echo $existingModelDetails | jq -r .properties.$calibrationError)
  existingDevSetpointRmse=$(echo $existingModelDetails | jq -r .properties.$devSetpointRmse)

  echo "Existing Calibration Error model rmse: $existingCalibrationErrorRmse"
  echo "Existing Dev Setpoint model rmse: $existingDevSetpointRmse"

  # If an existing model is found, compare models
  if [ -z "$existingModelDetails" ]
  then
    printf "\nExisting model not found!"
  else
    compareModels $resourceGroup $workspace $currentCalibrationErrorRmse $currentDevSetpointRmse $existingCalibrationErrorRmse $existingDevSetpointRmse $existingModelId
  fi

  # Tag current model as best
  printf "\nAdd tag label to current model"
  az ml model update \
    --model-id $currentModelId \
    --add-tag label=$labelName \
    --resource-group $resourceGroup \
    --workspace-name $workspace

  if [ $? -eq 0 ]; then
      printf "\nSuccessfully tagged current model with the best model label.\n"
  else
      printf "\nSomething went wrong when trying to tag the current model. Attempting to restore tag to existing model...\n"

      az ml model update \
        --model-id $existingModelId \
        --add-tag label=$labelName \
        --resource-group $resourceGroup \
        --workspace-name $workspace

      exit 1
  fi
}

# Exit program if we don't get arguments
[[ $opts_count < 9 ]] && { usage && exit 1; } || start
