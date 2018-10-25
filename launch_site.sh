#!/usr/bin/zsh
docker build -t dilbert-viewer . && \
docker run -d -p 8080:80 --rm --name "dilbert" dilbert-viewer && \
echo "Dilbert Viewer running as docker container with name: dilbert" && \
xdg-open "http://localhost:8080"
