#!/bin/bash

opts_count=0
while getopts l:f: flag
do
    case "${flag}" in
        l)                           modelLabel=${OPTARG}; ((opts_count=opts_count+1)) ;;
        f)                           configFile=${OPTARG}; ((opts_count=opts_count+1)) ;;
        *)                                     echo "Unknown parameter passed"; exit 1 ;;
    esac
done

usage(){
    echo "**Prepare Model Label Script***"
    echo "Usage: ./prepare_model_label.sh -l best_recommendation -f config/config.json"
    echo "---Parameters---"
    echo "l=    :model label"
    echo "f=    :model config file e.g. config/config.json"
}

prepareModelLabel () {
  local label=$1
  local configName=$2


  # Remove '/' from path if exists
  if [[ "$configName" == *"/"* ]]; then
    configName=$(echo $configName | awk -F"/" '{print $NF}')
  fi

  # Remove '.' from path if exists
  if [[ "$configName" == *"."* ]]; then
    configName=$(echo $configName | cut -f1 -d".")
  fi

  labelName="$label"_"$configName"
  echo $labelName
}

start () {
  # Creates labelName variable using config name
  prepareModelLabel $modelLabel $configFile
}

# Exit program if we don't get arguments
[[ $opts_count < 2 ]] && { usage && exit 1; } || start
