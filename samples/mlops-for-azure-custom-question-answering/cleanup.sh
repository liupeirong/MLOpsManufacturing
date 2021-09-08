#!/bin/bash

echo "Deleting Custom Question Answering resources..."
az deployment sub delete --name deployCQAMLOpsExample
az deployment sub delete --name custom-question-answering-rg
az group delete --resource-group custom-question-answering-rg