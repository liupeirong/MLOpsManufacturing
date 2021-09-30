#!/bin/bash

./copy_files.sh
python -m grpc_tools.protoc -I protos protos/*.proto --grpc_python_out=protos --python_out=protos
