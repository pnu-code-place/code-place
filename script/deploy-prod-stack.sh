#!/bin/bash

STACK_NAME="code-place-prod"

sudo docker stack deploy -c ../deployment/docker-compose.yml -c ../deployment/docker-compose.prod.yml $STACK_NAME
