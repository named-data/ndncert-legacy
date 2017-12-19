#!/bin/bash

docker rm ndnop-process-request-runner 2>/dev/null || true
docker create --name ndnop-process-request-runner -ti --rm -e HOME=/home --net=host ndnop:latest /usr/bin/ndnop-process-requests >/dev/null
docker cp $HOME/.ndn ndnop-process-request-runner:/home/

docker start -ia ndnop-process-request-runner
