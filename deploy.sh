#!/bin/bash

eval "$(ssh-agent -s)" &&
ssh-add -k ~/.ssh/id_rsa &&
# cd /coba/www/Portofolio-E-Commerce-Backend
# git pull

source ~/.profile
echo "$DOCKER_PASSWORD" | docker login --username $DOCKER_USERNAME --password-stdin
sudo docker stop sevoucher-be
sudo docker rm sevoucher-be
sudo docker rmi alulfazlur/sevoucher-be:latest
sudo docker run -d --name sevoucher-be -p 9000:9000 alulfazlur/sevoucher-be:latest
