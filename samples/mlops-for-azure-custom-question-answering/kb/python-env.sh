# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

conda create -n $1 -y
activate $1
pip install --upgrade --no-cache-dir -r $2