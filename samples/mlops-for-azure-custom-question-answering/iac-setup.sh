#!/bin/bash

if [ -n "$1" ]; then
    # Locations are limited while in preview
    az deployment sub create -l northeurope -f ./iac/main.bicep --name deployCQAMLOpsExample --parameters salt=$1 location=northeurope

    # Init .env file
    printf "" > .env

    # Populate Endpoint and Key for first Custom Question Answering Service
    ENDPOINT_EDIT=$(az deployment sub show \
                    -n deployCQAMLOpsExample \
                    --query properties.outputs.cqa1_endpoint.value)
    KEY_EDIT=$(az deployment sub show \
                    -n deployCQAMLOpsExample \
                    --query properties.outputs.cqa1_key.value)

    # Populate Endpoint and Key for second Custom Question Answering Service
    ENDPOINT_PROD=$(az deployment sub show \
                    -n deployCQAMLOpsExample \
                    --query properties.outputs.cqa2_endpoint.value)
    KEY_PROD=$(az deployment sub show \
                    -n deployCQAMLOpsExample \
                    --query properties.outputs.cqa2_key.value)

    # Storage Account
    AZURE_STORAGE_ACCOUNT=$(az deployment sub show \
                    -n deployCQAMLOpsExample \
                    --query properties.outputs.storage_account.value)
    SAS_TOKEN=$(az deployment sub show \
                    -n deployCQAMLOpsExample \
                    --query properties.outputs.storage_sas.value)

    # Append to ENV
    printf "#### Please exchange the values as described in README.md #####\n\n" >> .env
    printf "AZURE_DEVOPS_EXT_GITHUB_PAT=''\n" >> .env
    printf "YOUR_GIT_HUB_ID=''\n" >> .env
    printf "YOUR_AZURE_DEV_OPS_ORG=''\n" >> .env
    printf "YOUR_AZURE_DEV_OPS_PROJECT_NAME=''\n" >> .env
    printf "\n#### Additional Config #####\n\n" >> .env
    printf "GIT_HUB_REPO_ID='MLOpsManufacturing'\n" >> .env
    printf "GIT_HUB_BRANCH='main'\n" >> .env
    printf "\n#### Values from IaC #####\n\n" >> .env
    printf "ENDPOINT_EDIT=$ENDPOINT_EDIT\n" >> .env
    printf "ENDPOINT_PROD=$ENDPOINT_PROD\n" >> .env
    printf "KEY_EDIT=$KEY_EDIT\n" >> .env
    printf "KEY_PROD=$KEY_PROD\n" >> .env
    printf "AZURE_STORAGE_ACCOUNT=$AZURE_STORAGE_ACCOUNT\n" >> .env
    echo "SAS_TOKEN=$SAS_TOKEN" >> .env

    # Post Deployment Knowledgebase Setup
    # EDIT
    export QNA_DEST_ENDPOINT=$(echo $ENDPOINT_EDIT | xargs)
    export QNA_DEST_SUB_KEY=$(echo $KEY_EDIT | xargs)
    result=$(python kb/scripts/create-kb.py --input data/init_en.json --name 'Editorial QnA EN')
    EDIT_KB_ID=$(echo $result | cut -d '#' -f 2)
    # PROD
    export QNA_DEST_ENDPOINT=$(echo $ENDPOINT_PROD | xargs)
    export QNA_DEST_SUB_KEY=$(echo $KEY_PROD | xargs)
    result=$(python kb/scripts/create-kb.py --input data/init_en.json --name 'Production QnA EN')
    PROD_KB_ID=$(echo $result | cut -d '#' -f 2)
    #
    printf "\n#### Values from Post Deployment #####\n\n" >> .env
    printf "EDIT_KB_ID=$EDIT_KB_ID\n" >> .env
    printf "PROD_KB_ID=$PROD_KB_ID\n" >> .env

else
    printf "Please enter a salt as parameter to create unique but stable names e.g. \n$>bash setup.sh myTest\n"
fi