#!/bin/bash

# Generate Python gRPC code from proto files

# Install grpcio-tools if not already installed
pip install grpcio-tools

# Create output directories
mkdir -p auth-service/app/grpc/generated
mkdir -p user-service/app/grpc/generated
mkdir -p gateway-service/app/grpc/generated

# Generate for auth-service
python -m grpc_tools.protoc \
  -I./proto \
  --python_out=./auth-service/app/grpc/generated \
  --grpc_python_out=./auth-service/app/grpc/generated \
  --pyi_out=./auth-service/app/grpc/generated \
  ./proto/common.proto ./proto/auth.proto ./proto/user.proto

# Generate for user-service
python -m grpc_tools.protoc \
  -I./proto \
  --python_out=./user-service/app/grpc/generated \
  --grpc_python_out=./user-service/app/grpc/generated \
  --pyi_out=./user-service/app/grpc/generated \
  ./proto/common.proto ./proto/auth.proto ./proto/user.proto

# Generate for gateway-service
python -m grpc_tools.protoc \
  -I./proto \
  --python_out=./gateway-service/app/grpc/generated \
  --grpc_python_out=./gateway-service/app/grpc/generated \
  --pyi_out=./gateway-service/app/grpc/generated \
  ./proto/common.proto ./proto/auth.proto ./proto/user.proto

# Create __init__.py files
touch auth-service/app/grpc/generated/__init__.py
touch user-service/app/grpc/generated/__init__.py
touch gateway-service/app/grpc/generated/__init__.py

echo "gRPC code generation complete!"
