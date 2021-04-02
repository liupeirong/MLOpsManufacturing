#!/bin/bash

# This script deploys a VM with iotedge setup

opts_count=0
while getopts e:p:r:v:n:a:u:k:d:f: flag
do
    case "${flag}" in
        e)                      environmentName=${OPTARG}; ((opts_count=opts_count+1)) ;;
        p)                          projectName=${OPTARG}; ((opts_count=opts_count+1)) ;;
        r)                        resourceGroup=${OPTARG}; ((opts_count=opts_count+1)) ;;
        v)                   virtualMachineName=${OPTARG}; ((opts_count=opts_count+1)) ;;
        n)                   virtualNetworkName=${OPTARG}; ((opts_count=opts_count+1)) ;;
        a)                   authenticationType=${OPTARG}; ((opts_count=opts_count+1)) ;;
        u)                        adminUsername=${OPTARG}; ((opts_count=opts_count+1)) ;;
        k)         adminPublicKeyPathOrPassword=${OPTARG}; ((opts_count=opts_count+1)) ;;
        d)               deviceConnectionString=${OPTARG}; ((opts_count=opts_count+1)) ;;
        f)                  cloudConfigFilePath=${OPTARG}; ((opts_count=opts_count+1)) ;;
        *)                                     echo "Unknown parameter passed"; exit 1 ;;
    esac
done

usage(){
    echo "***Edge VM Deployment Script***"
    echo "Usage: ./deployEdgeVM.sh -e dev -p eod -r myRg -v myVM -n myVnet -a password -u edgeadmin -k Password@123 -d \"HostName=iot.azure.devices.net;DeviceId=\" -f cloud-config.yml"
    echo "---Parameters--- "
    echo "e=    :environment tag value i.e. 'dev', 'prod"
    echo "p=    :project name tag value"
    echo "r=    :resource group name"
    echo "v=    :virtual machine name"
    echo "n=    :virtual network name"
    echo "a=    :authentication type, must be 'password' or 'ssh'"
    echo "u=    :admin username"
    echo "k=    :admin password or ssh public key file path"
    echo "d=    :IoT device connection string"
    echo "f=    :file path to the cloud-config.yml file"
}

vmImage='Canonical:UbuntuServer:18.04-LTS:latest'
vmSize='Standard_DS1_v2'

deployVM() {
  # Sometimes a '/'' is present in the connection string and it breaks sed, this escapes the '/'
  DEVICE_CONNECTION_STRING=${deviceConnectionString//\//\\/}

  # If running this script outside of linux, you need to add an empty string after the -i
  # https://myshittycode.com/2014/07/24/os-x-sed-extra-characters-at-the-end-of-l-command-error/
  sed -i "s/xDEVICE_CONNECTION_STRINGx/${DEVICE_CONNECTION_STRING//\"/}/g" $cloudConfigFilePath
  sed -i "s/xADMIN_USERNAMEx/${adminUsername}/g" $cloudConfigFilePath

  if [ $authenticationType == 'password' ]; then
    az vm create \
          --name $virtualMachineName \
          --resource-group $resourceGroup \
          --size $vmSize \
          --image $vmImage \
          --vnet-name $virtualNetworkName \
          --authentication-type $authenticationType \
          --admin-username $adminUsername \
          --admin-password $adminPublicKeyPathOrPassword \
          --public-ip-address "" \
          --subnet 'edgeVmSubnet' \
          --subnet-address-prefix 10.0.1.0/24 \
          --tags Environment=$environmentName Project=$projectName \
          --custom-data $cloudConfigFilePath
  else [ $authenticationType == 'ssh' ]
    az vm create \
          --name $virtualMachineName \
          --resource-group $resourceGroup \
          --size $vmSize \
          --image $vmImage \
          --vnet-name $virtualNetworkName \
          --authentication-type $authenticationType \
          --admin-username $adminUsername \
          --ssh-key-values $adminPublicKeyPathOrPassword \
          --public-ip-address "" \
          --subnet 'edgeVmSubnet' \
          --subnet-address-prefix 10.0.1.0/24 \
          --tags Environment=$environmentName Project=$projectName \
          --custom-data $cloudConfigFilePath
  fi
}

# Exit program if we don't get 10 arguments
[[ $opts_count < 10 ]] && { usage && exit 1; } || deployVM
