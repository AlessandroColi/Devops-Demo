#!/bin/bash

docker stop staging-app 2>/dev/null || true
docker rm staging-app 2>/dev/null || true

docker run -d --name staging-app -p 8080:80 demo-app:latest