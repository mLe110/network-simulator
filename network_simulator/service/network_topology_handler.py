import logging
import copy

from network_simulator.exceptions.network_topology_handler_exception import InvalidDeviceTypeException, \
    InvalidNetworkTopologyException


def process_network_topology(registered_devices, topology_json):
    logger = logging.getLogger(__name__)
    logger.info("Process network topology json.")
    validate_network_device_ids(topology_json)
    return enrich_json_topology(registered_devices, topology_json)


def validate_network_device_ids(topology_json):
    logger = logging.getLogger(__name__)
    logger.debug("Validate network device ids in network topology json.")
    device_id_list = [device["device_id"] for device in topology_json["devices"]]

    for network in topology_json["network"]:
        if not all(device in device_id_list for device in network["devices"]):
            raise InvalidNetworkTopologyException("Network '{}' contains device which is "
                                                  "not part of the devices list.".format(network))

    return True


def enrich_json_topology(registered_devices, topology_json):
    logger = logging.getLogger(__name__)
    logger.debug("Add device data (VIoTD type, tap interface name) to network topology json.")
    enriched_json = {
        "devices": [],
        "network": copy.deepcopy(topology_json["network"])
    }

    for device in topology_json["devices"]:
        copied_device = copy.deepcopy(device)
        if device["device_id"] in registered_devices.keys():
            if "type" in device:
                raise InvalidDeviceTypeException("Device in JSON has type {}, but is a tap device.".format(device["type"]))

            copied_device["type"] = registered_devices[device["device_id"]]["device_type"]
            copied_device["tap_if_name"] = registered_devices[device["device_id"]]["tap_if_name"]
        enriched_json["devices"].append(copied_device)

    return enriched_json
