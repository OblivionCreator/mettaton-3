docker system prune
docker build -t mettaton-3-new .
docker save mettaton-3 -o ~/docker-store/mettaton-3-new.tar
