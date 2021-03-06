#!/bin/bash

VERSION=$(cat ../deter-report/COMPONENT_VERSION | grep -oP '(?<="version": ")[^"]*')
export VERSION

# build all images
docker build -t terrabrasilis/deter-report:v$VERSION --build-arg VERSION=$VERSION -f Dockerfile ../

# send to dockerhub
echo "The building was finished! Do you want sending this new image to Docker HUB? Type yes to continue." ; read SEND_TO_HUB
if [[ ! "$SEND_TO_HUB" = "yes" ]]; then
    echo "Ok, not send the image."
else
    echo "Nice, sending the image!"
    docker push terrabrasilis/deter-report:v$VERSION
fi