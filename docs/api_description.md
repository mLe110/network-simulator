## Overview

The network-simulator service exposes three different kinds of REST APIs. The VIoTD API is for virtualized IoT devices to register/deregister themselves. Registering means that a VIoTD wants to participate in the future simulation. VIoTDs, which have not registered themselves at the network-simulator service, cannot participate in a simulation. The second API is the Simulation API. These endpoints are designated to the simulation platform and can be used to start and stop the simulation. The third API manages libvirt networks and can be used to create and remove libvirt networks.

The base URL for all APIs is "http://host:port/api/v1".

### VIoTD API
#### Register device
This endpoint is for devices to register themselves at the network simulator.

HTTP Method: `POST`
Resource URL: `/register`
Payload:
```json
{
  "device_id": The unique ID of the device,
  "device_type": Whether the device is a VM, container or process,
  "tap_if_name": The name of the tap interface used by the device
}
```

The response contains the name of the network namespace ns-3 is running in. An example is
```json
{
  "ns_namespace": "testNamespace"
}
```

#### Deregister device
A device has to deregister if it leaves the setup, so that the network-simulator service is informed that this device will not participate in any future simulation. It is important to mention that these steps need to be done before a simulation starts, i.e. a device cannot deregister itself during the simulation.

HTTP Method: `DELETE`
Resource URL: `/deregister/<device_id>`

The endpoint responds with the HTTP status code 200 if the request was successful. Otherwise, a proper error message is returned.



### Simulation API
#### Start simulation
This endpoint starts ns-3. It creates the submitted network topology and establishes the channels between devices. 

HTTP Method: `POST`
Resource URL: `/simulation/start`
Payload:
The payload represents the network topology for the simulator in a JSON format. It contains a list of devices with device specific configuration options and a list of networks, providing information about the connection between devices. Due to the variety of parameters and values, the description of the network JSON is in the `network_topology.json` file in the `docs` folder. It provides a detailed explanation about the JSON structure, possible parameters and allowed values. Further, examples can be found in the `network_examples` directory.

The endpoint responds with the HTTP status code 200 if the request was successful. Otherwise, a proper error message is returned.

#### Stop simulation
This endpoint stops the network simulation.

HTTP Method: `GET`
Resource URL: `/simulation/stop`

The endpoint responds with the HTTP status code 200 if the request was successful. Otherwise, a proper error message is returned. If the simulation is not running and this endpoint is called, a response with status code 400 will be returned.



### Libvirt Network API
#### Create libvirt network
This endpoint creates a new libvirt network for VM devices according to the configuration provided in the payload.

HTTP Method: `POST`
Resource URL: `/network/create`
Payload:
```json
{
  "network_name": The name of the network.
  "gateway_ip": The IP subnet of the network as string.
  "netmask": The netmask of the subnet as string. 
  "start_ip": The lowest IP address the DHCP server should assign to any device joining the network. 
  "end_ip": The highest IP address the DHCP server should assign to any device joining the network.
}
```

The endpoint responds with the HTTP status code 200 if the request was successful. Otherwise, a proper error message is returned.


#### Remove libvirt network
This endpoint removes a previously created libvirt network. This endpoint does not consider devices connected to the network. If the network is removed while devices are still connected, these devices will lose their connectivity.

HTTP Method: `DELETE`
Resource URL: `/network/remove/<network_name>`

The endpoint responds with the HTTP status code 200 if the request was successful. Otherwise, a proper error message is returned.




