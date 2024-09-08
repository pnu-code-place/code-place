#!/bin/bash

STACK_NAME="code-place-dev"

sudo docker stack deploy -c ../deployment/docker-compose.yml -c ../deployment/docker-compose.dev.yml $STACK_NAME
