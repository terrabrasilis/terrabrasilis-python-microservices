#!/bin/bash

VERSION=$(cat ../deter-sar-ftp-download/PROJECT_VERSION | grep -oP '(?<="version": ")[^"]*')
export VERSION

# build all images
docker build -t terrabrasilis/deter-sar-ftp-download:v$VERSION --build-arg VERSION=$VERSION -f Dockerfile ../

# send to dockerhub
echo "The building was finished! Do you want sending this new image to Docker HUB? Type yes to continue." ; read SEND_TO_HUB
if [[ ! "$SEND_TO_HUB" = "yes" ]]; then
    echo "Ok, not send the image."
else
    echo "Nice, sending the image!"
    docker push terrabrasilis/deter-sar-ftp-download:v$VERSION
fi