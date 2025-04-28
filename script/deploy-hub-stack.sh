#!/bin/bash

STACK_NAME="code-place-hub"

sudo docker stack deploy -c ../deployment/docker-compose.hub.yml $STACK_NAME
