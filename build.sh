docker system prune
docker build -t mettaton-3 .
docker save mettaton-3 -o ~/docker-store/mettaton-3.tar