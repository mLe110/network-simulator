from unittest import TestCase

from network_simulator.exceptions.network_topology_handler_exception import InvalidDeviceTypeException, \
    InvalidNetworkTopologyException
from network_simulator.service.network_topology_handler import enrich_json_topology, validate_network_device_ids


class TestNetworkTopologyHandler(TestCase):
    def setUp(self):
        self.registered_devices = {
            "viotd-id": {
                "device_id": "viotd-id",
                "device_type": "vm",
                "tap_if_name": "tap-viotd-id"
            }
        }
        self.topology_devices_json = {
            "devices": [{
                "device_id": "viotd-id",
            }],
            "network": []
        }
        self.topology_json = {
            "devices": [{
                "device_id": "switch",
                "type": "bridge"
            }],
            "network": [{
                "network_type": "CSMA",
                "general_config": {
                    "data_rate": "512kbps",
                    "delay": "10ms"
                },
                "address": {
                    "ip": "10.1.1.0",
                    "netmask": "255.255.255.0"
                },
                "devices": ["viotd-id", "switch1"]
            }]
        }

    def test_validateJsonWithMissingDeviceId(self):
        with self.assertRaises(InvalidNetworkTopologyException):
            validate_network_device_ids(self.topology_json)

    def test_validateJsonWithValidNetwork(self):
        self.topology_json["devices"].append(self.topology_devices_json["devices"][0])
        validate_network_device_ids(self.topology_devices_json)

    def test_enrichDeviceTypeSuccessfully(self):
        enriched_json = enrich_json_topology(self.registered_devices, self.topology_devices_json)
        self.assertEqual(self.registered_devices["viotd-id"]["device_type"], enriched_json["devices"][0]["type"])

    def test_enrichTapIfNameSuccessfully(self):
        enriched_json = enrich_json_topology(self.registered_devices, self.topology_devices_json)
        self.assertEqual(self.registered_devices["viotd-id"]["tap_if_name"], enriched_json["devices"][0]["tap_if_name"])

    def test_failIfTapHasRouterType(self):
        self.topology_devices_json["devices"][0]["type"] = "router"
        with self.assertRaises(InvalidDeviceTypeException):
            enrich_json_topology(self.registered_devices, self.topology_devices_json)

    def test_failIfTapHasBridgeType(self):
        self.topology_devices_json["devices"][0]["type"] = "bridge"
        with self.assertRaises(InvalidDeviceTypeException):
            enrich_json_topology(self.registered_devices, self.topology_devices_json)

    def test_enrichDeviceKeepsNetwork(self):
        enriched_json = enrich_json_topology(self.registered_devices, self.topology_json)
        self.assertEqual(self.topology_json["network"], enriched_json["network"])






#        self.topology_json = """
#            {
#                "devices": [{
#                    "device_id": "tap-container1",
#                    "type": "container"
#                }, {
#                    "device_id": "tap-container2",
#                    "type": "container"
#                }, {
#                    "device_id": "switch1",
#                    "type": "switch"
#                }],
#                "network": [{
#                    "network_type": "CSMA",
#                    "general_config": {
#                        "data_rate": "512kbps",
#                        "delay": "10ms"
#                    },
#                    "address": {
#                        "ip": "10.1.1.0",
#                        "netmask": "255.255.255.0"
#                    },
#                    "devices": [ "tap-container1", "switch1"]
#                }, {
#                    "network_type": "CSMA",
#                    "general_config": {
#                        "data_rate": "512kbps",
#                        "delay": "10ms"
#                    },
#                    "address": {
#                        "ip": "10.1.1.0",
#                        "netmask": "255.255.255.0"
#                    },
#                    "devices": [ "tap-container2", "switch1"]
#                }]
#            }
#        """
