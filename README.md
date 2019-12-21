# network-simulator

With the following command, the network-service container can be started:
```
docker run --rm -d --cap-add NET_ADMIN --device /dev/net/tun:/dev/net/tun --mount type=bind,source=/var/run/netns,target=/var/run/netns -p 5000:5000 3012c4502fbe
```

