# Docker Image which is used as foundation to create
# a custom Docker Image with this Dockerfile
FROM node:latest

ENV APP_DIR=/usr/src/app

# A directory within the virtualized Docker environment
# Becomes more relevant when using Docker Compose later
WORKDIR /usr/src/app

# Copies package.json and package-lock.json to Docker environment
COPY package*.json ./

# Installs all node packages
RUN npm install

# Copies everything over to Docker environment
COPY . .

RUN sed -i 's/\r$//g' /usr/src/app/scripts/entrypoint.sh
RUN chmod +x /usr/src/app/scripts/entrypoint.sh
ENTRYPOINT ["/bin/bash", "/usr/src/app/scripts/entrypoint.sh"]