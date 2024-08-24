#!/bin/sh

base=/CSEP_FE

build_vendor_dll()
{
  if [ ! -e "${base}/build/vendor-manifest.json" ]
  then
      npm run build:dll
  fi
}
cd $base
build_vendor_dll && \
npm run build

if [ $? -ne 0 ]; then
    echo "Build error, please check node version and package.json"
    exit 1
fi

exec nginx -c /CSEP_FE/deploy/nginx.conf
