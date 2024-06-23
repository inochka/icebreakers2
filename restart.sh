sudo docker stop $(sudo docker ps -a -q)
sudo docker system prune
sudo docker rmi -f $(sudo docker images -a -q)
git fetch
git pull --rebase
sudo docker compose -f docker-compose.yml up -d