#!/bin/bash
docker build -t haavardnk/beermonopoly-api .   
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
docker push haavardnk/beermonopoly-api