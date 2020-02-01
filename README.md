# Virtualization of ``Internet of Things`` Devices - Network Simulator

This repository is part of a Master's thesis and further, contributes to the research efforts at the University of Illinois at Urbana-Champaign (UIUC) to develop a flexible end-to-end simulation platform for the IoT. The network simulator consists of the network service and [ns-3](https://www.nsnam.org/). The network service exposes a REST API to control the network simulator, and ns-3 simulates communication channels between virtual devices to mimic real-world characteristics for data transmission. To simplify the setup process of the network simulator, a docker image was created and published to [dockerhub](https://hub.docker.com/repository/docker/mle110/ns), which includes the network service and ns-3. 

As the network simulator container requires certain priviliges, e.g. for creating tap interfaces and bridges, a python script to run and stop the setup is provided in the `run_scripts` folder. 

After running the container, it exposes a REST API for managing its networks. The API description can be found in the `docs` folder. Further, network topologies are represented in JSON structures. To simulate a network topology at runtime, the corresponding JSON needs to be submitted to the simulation endpoint. The description of the JSON format can be found in the `docs` folder and the `network_examples` directory provides basic network topologies in their JSON representation.

