#!/bin/bash

# Create Environment
bash kb/python-env.sh devenv kb/pip-requirements.txt
# Prepare Bash
conda init bash
