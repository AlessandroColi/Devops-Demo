#!/bin/bash

docker build -t demo-app:latest ./app

docker tag demo-app:latest demo-app:$(date +%Y%m%d-%H%M%S)