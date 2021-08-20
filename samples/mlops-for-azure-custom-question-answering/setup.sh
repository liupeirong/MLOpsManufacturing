#!/bin/bash

if [ -n "$1" ]; then
    # Locations are limited while in preview
    az deployment sub create -l northeurope -f ./iac/main.bicep --name deployCQAMLOpsExample --parameters salt=$1 location=northeurope

    # Init .env file
    printf "" > .env

    # Populate Endpoint and Key for first Custom Question Answering Service
    ENDPOINT_EDIT=$(az deployment group show \
                    -g custom-question-answering-rg \
                    -n customQuestionAnsweringEdit \
                    --query properties.outputs.endpoint.value)
    KEY_EDIT=$(az deployment group show \
                    -g custom-question-answering-rg \
                    -n customQuestionAnsweringEdit \
                    --query properties.outputs.key.value)

    # Populate Endpoint and Key for second Custom Question Answering Service
    ENDPOINT_PROD=$(az deployment group show \
                    -g custom-question-answering-rg \
                    -n customQuestionAnsweringProd \
                    --query properties.outputs.endpoint.value)
    KEY_PROD=$(az deployment group show \
                    -g custom-question-answering-rg \
                    -n customQuestionAnsweringProd \
                    --query properties.outputs.key.value)

    # Append to ENV
    printf "ENDPOINT_EDIT=$ENDPOINT_EDIT\n" >> .env
    printf "ENDPOINT_PROD=$ENDPOINT_PROD\n" >> .env
    printf "KEY_EDIT=$KEY_EDIT\n" >> .env
    printf "KEY_PROD=$KEY_PROD\n" >> .env

else
    printf "Please enter a salt as parameter to create unique but stable names e.g. \n$>bash setup.sh myTest\n"
fi