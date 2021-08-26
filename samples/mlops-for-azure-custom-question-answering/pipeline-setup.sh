#!/bin/bash
## Azure Pipelines Setup Script

# load configuration from IaC script
export $(cat .env | grep -v '#' | xargs) 

service_connection_id=$(az devops service-endpoint github create \
--github-url https://github.com/$YOUR_GIT_HUB_ID/$GIT_HUB_REPO_ID/ \
--name github \
--organization https://dev.azure.com/$YOUR_AZURE_DEV_OPS_ORG \
--project $YOUR_AZURE_DEV_OPS_PROJECT_NAME \
-o tsv --query 'id')

az pipelines create \
--name 'Train & Deploy' \
--description 'Executes accuracy test in EDIT environment and deploys result to PROD' \
--repository https://github.com/$YOUR_GIT_HUB_ID/$GIT_HUB_REPO_ID/ \
--branch $GIT_HUB_BRANCH \
--yml-path samples/mlops-for-azure-custom-question-answering/devops_pipelines/kb/KB-CD-Manual.yml \
--organization https://dev.azure.com/$YOUR_AZURE_DEV_OPS_ORG \
--project $YOUR_AZURE_DEV_OPS_PROJECT_NAME \
--service-connection $service_connection_id

az pipelines create \
--name 'Train Only' \
--description 'Executes accuracy test in EDIT environment without deploying to PROD' \
--repository https://github.com/$YOUR_GIT_HUB_ID/$GIT_HUB_REPO_ID/ \
--branch $GIT_HUB_BRANCH \
--yml-path samples/mlops-for-azure-custom-question-answering/devops_pipelines/kb/KB-Train-only.yml \
--organization https://dev.azure.com/$YOUR_AZURE_DEV_OPS_ORG \
--project $YOUR_AZURE_DEV_OPS_PROJECT_NAME \
--service-connection $service_connection_id

az pipelines create \
--name 'Deploy Previous' \
--description 'Loads specific version and deploying to PROD' \
--repository https://github.com/$YOUR_GIT_HUB_ID/$GIT_HUB_REPO_ID/ \
--branch $GIT_HUB_BRANCH \
--yml-path samples/mlops-for-azure-custom-question-answering/devops_pipelines/kb/KB-CD-PreviousVersion.yml \
--organization https://dev.azure.com/$YOUR_AZURE_DEV_OPS_ORG \
--project $YOUR_AZURE_DEV_OPS_PROJECT_NAME \
--service-connection $service_connection_id

az pipelines create \
--name 'Merge Active Learning Feedback' \
--description 'Loads Active Learning Feedback from PROD and merges it to EDIT environment' \
--repository https://github.com/$YOUR_GIT_HUB_ID/$GIT_HUB_REPO_ID/ \
--branch $GIT_HUB_BRANCH \
--yml-path samples/mlops-for-azure-custom-question-answering/devops_pipelines/al/AL-Merge-Manual.yml \
--organization https://dev.azure.com/$YOUR_AZURE_DEV_OPS_ORG \
--project $YOUR_AZURE_DEV_OPS_PROJECT_NAME \
--service-connection $service_connection_id

vg_edit_settings_id=$(az pipelines variable-group create \
--name 'QNA_EDIT_SETTINGS' \
--description 'Settings for QNA Maker EDIT environment' \
--variables QNA_ENDPOINT_HOST=$ENDPOINT_EDIT, QNA_KB_ID=$EDIT_KB_ID \
--organization https://dev.azure.com/$YOUR_AZURE_DEV_OPS_ORG \
--project $YOUR_AZURE_DEV_OPS_PROJECT_NAME \
--query 'id')

vg_prod_settings_id=$(az pipelines variable-group create \
--name 'QNA_PROD_SETTINGS' \
--description 'Settings for QNA Maker PROD environment' \
--variables QNA_ENDPOINT_HOST=$ENDPOINT_PROD, QNA_KB_ID=$PROD_KB_ID \
--organization https://dev.azure.com/$YOUR_AZURE_DEV_OPS_ORG \
--project $YOUR_AZURE_DEV_OPS_PROJECT_NAME \
--query 'id')

vg_store_settings_id=$(az pipelines variable-group create \
--name 'STORAGE_SETTINGS' \
--description 'Storage Account Settings' \
--variables AZURE_STORAGE_ACCOUNT=$AZURE_STORAGE_ACCOUNT \
--organization https://dev.azure.com/$YOUR_AZURE_DEV_OPS_ORG \
--project $YOUR_AZURE_DEV_OPS_PROJECT_NAME \
--query 'id')

az pipelines variable-group create \
--name 'ACCURACY_TEST_SETTINGS' \
--description 'Accuracy Test Settings' \
--variables TOP_ANSWER=3, TOP_PROMPT=3, SCORE_THRESHOLD=0.3, SCORE_SIMILARITY=0.5, MULTI_TURN_DEPTH=3, PRECISE_ANSWERING=False, TEST_FAIL_THRESHOLD=80 \
--organization https://dev.azure.com/$YOUR_AZURE_DEV_OPS_ORG \
--project $YOUR_AZURE_DEV_OPS_PROJECT_NAME

az pipelines variable-group variable create \
--group-id $vg_edit_settings_id \
--name 'QNA_ENDPOINT_KEY' \
--value $KEY_EDIT \
--secret \
--organization https://dev.azure.com/$YOUR_AZURE_DEV_OPS_ORG \
--project $YOUR_AZURE_DEV_OPS_PROJECT_NAME

az pipelines variable-group variable create \
--group-id $vg_prod_settings_id \
--name 'QNA_ENDPOINT_KEY' \
--value $KEY_PROD \
--secret \
--organization https://dev.azure.com/$YOUR_AZURE_DEV_OPS_ORG \
--project $YOUR_AZURE_DEV_OPS_PROJECT_NAME

az pipelines variable-group variable create \
--group-id $vg_store_settings_id \
--name 'AZURE_STORAGE_SAS_TOKEN' \
--value $SAS_TOKEN \
--secret \
--organization https://dev.azure.com/$YOUR_AZURE_DEV_OPS_ORG \
--project $YOUR_AZURE_DEV_OPS_PROJECT_NAME