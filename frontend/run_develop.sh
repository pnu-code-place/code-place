#!/bin/bash

default_proxy="http://localhost:8000"
export NODE_ENV=development

if ["$1" == "--proxy"]; then
  proxy_ip="$2"
  echo "Proxy IP is $proxy_ip"
  export TARGET=$proxy_ip
else
  echo "Running Default Proxy Backend"
  export TARGET=$default_proxy
fi

npm run dev
