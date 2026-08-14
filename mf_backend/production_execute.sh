echo "Deploying the build"
sudo docker ps -a

sudo docker stop radian_app
sudo docker rm radian_app
sudo docker rmi radian_app:development

cd /home/radian/radian-los-backend
git pull
git checkout production
git pull

sudo docker compose -f docker/docker-compose.yml up -d
