#!/bin/bash

eval "$(ssh-agent -s)" &&
ssh-add -k ~/.ssh/id_rsa &&
# cd /coba/www/Portofolio-E-Commerce-Backend
# git pull

source ~/.profile
echo "$DOCKER_PASSWORD" | docker login --username $DOCKER_USERNAME --password-stdin
docker stop flaskdemo
docker rm flaskdemo
docker rmi alulfazlur/flask-tutorial:latest
docker run -d --name flaskdemo -p 9000:9000 alulfazlur/flask-tutorial:latest
