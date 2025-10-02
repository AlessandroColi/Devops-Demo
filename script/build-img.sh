#!/bin/bash

# Build the image once
docker build -t demo-app:latest ./app

# Tag it with timestamp for versioning
docker tag demo-app:latest demo-app:$(date +%Y%m%d-%H%M%S)