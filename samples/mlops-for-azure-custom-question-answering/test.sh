#!/bin/bash
## Azure Pipelines Setup Script

# load configuration from IaC script
export $(cat .env | grep -v '#' | xargs) 

export QNA_DEST_ENDPOINT=$ENDPOINT_EDIT
export QNA_DEST_SUB_KEY=$KEY_EDIT

#result=$(python kb/scripts/create-kb.py --input data/init.json --name 'CreatePY')
result=$(python kb/scripts/create-kb.py --input data/init.json --name 'CreatePY')
echo $result
kb_id=$(echo $result | cut -d '#' -f 2)
#awk '/KB with ID/ {print $1}'
echo "KB ID IS: $kb_id"