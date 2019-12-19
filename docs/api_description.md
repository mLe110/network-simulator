## Overview

The network-simulator service exposes two different kinds of REST APIs. The VIoTD API is for virtualized IoT devices to register/unregister themselves. Registering means that a VIoTD wants to participate in the future simulation. VIoTDs, which have not registered themselves at the network-simulator service, cannot participate in a simulation.
The second API is the Simulation API. These endpoints are designated to the simulation platform and can be used to start the simulation and to set required device coordinates for wireless setups.

The base URL for all APIs is "http://host:port/api/v1".

### VIoTD API
#### Register device
To register a device, issue a POST request to "/register". The device ID, the name of the tap interface and the device type must be provided in the paylod. An example payload is

```json
{
  "device_id":"testDeviceId",
  "device_type": "vm",
  "tap_if_name":"tap-testDeviceId"
}
```

The response contains the name of the network namespace ns-3 is running in. An example is
```json
{
  "ns_namespace": "testNamespace"
}
```

#### Unregister device
A device has to unregister if it leaves the setup, so that the network-simulator service is informed that this device will not participate in any future simulation. It is important to mention that these steps need to be done before a simulation starts, i.e. a device cannot unregister itself during the simulation.
To unregister a device, issue a DELETE request to "/unregister/<device_id>", where <device_id> is the ID used by the device to register itself previously. If the device was successfully unregistered, the status code 200 is returned. Otherwise, a proper status code with an error message.

In case the request fails, a possible error response looks like the following:
```json
{
  "error": {
    "type": "UnknownDeviceException",
    "message": "Cannot unregister device 'unknownID'."
  }
}
```
In this specific case, the status code would be 400 (bad request).


### Simulation API
#### Start simulation
To start the simulation, issue a POST request to "/simulate". The request payload contains the coordinates for each VIoTD which participates in the simulation. The current implementation requires that the registered devices match with the devices list in the request payload.

For example, if three devices with the IDs "deviceID1", "deviceID2", and "deviceID3" have already registered themselves, the payload for this endpoint would look similar to the following.
```json
[{
  "device_id": "deviceID1",
  "xpos": 4.0,
  "ypos": 3.5
}, {
  "device_id": "deviceID2",
  "xpos": 1.0,
  "ypos": 5.0
}, {
  "device_id": "deviceID3",
  "xpos": 10.0,
  "ypos": 10.0 
}
]
```
For the parameters "xpos" and "ypos", the values specify their coordinates in meters.

If something goes wrong, e.g. the list contains a device which is not registered at the network-simulator, the a response with status code 400 is returned and the error response looks like the following.

```json
{
  "error": {
    "type": "UnknownDeviceException",
    "message": "Cannot unregister device 'unknownID'."
  }
}
```
