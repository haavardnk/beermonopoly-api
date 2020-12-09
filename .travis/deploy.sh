#!/bin/bash
docker build -t haavardnk/vinmonopolet-x-untappd .   
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
docker push haavardnk/vinmonopolet-x-untappd