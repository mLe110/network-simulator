import json
from unittest.mock import Mock, patch

from network_simulator.test.controller.base_api import TestBaseApi, BASE_URL


class TestViotdApi(TestBaseApi):
    def setUp(self):
        super().setUp()
        self.app.application.net_sim_service.start_ns3 = Mock(return_value=None)
        self.app.application.net_sim_service.write_device_config = Mock(return_value=None)
        self.mock_libvirt_service = Mock()
        self.app.application.libvirt_network_service = self.mock_libvirt_service
        self.device1 = {"device_id": "viotd-id", "device_type": "vm", "tap_if_name": "tap1"}
        self.topology_devices_json = {
            "devices": [],
            "network": []
        }
        self.topology_json = {
            "devices": [{
                "device_id": "switch1",
                "type": "bridge"
            }, {
                "device_id": "viotd-id",
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

    def test_startSimulationWithNoDevices(self):
        response = self.app.post(BASE_URL + "/simulation/start",
                                 data=json.dumps([]),
                                 content_type="application/json")
        self.assertEqual(400, response.status_code)

    def test_startSimulationWithNone(self):
        response = self.app.post(BASE_URL + "/simulation/start",
                                 data=json.dumps(None),
                                 content_type="application/json")
        self.assertEqual(400, response.status_code)

    @patch("network_simulator.service.network_topology_handler.write_network_topology_to_file")
    def test_startSimulationWithTwoDevices(self, mock_write_topology):
        self.register_device(self.device1)
        self.app.application.net_sim_service.start_ns3 = Mock(return_value=None)
        shutdown_mock = Mock(return_value=None)
        self.mock_libvirt_service.shutdown_all_networks = shutdown_mock
        response = self.app.post(BASE_URL + "/simulation/start",
                                 data=json.dumps(self.topology_json),
                                 content_type="application/json")
        self.assertEqual(200, response.status_code)
        self.assertEqual(b"DONE", response.get_data())
        shutdown_mock.assert_called_once()

    @patch("network_simulator.service.network_simulator_service.os")
    def test_stopSimulationWhenNs3Running(self, mock_os):
        self.app.application.net_sim_service.proc = Mock()
        setup_network_mock = Mock(return_value=None)
        self.mock_libvirt_service.setup_all_networks = setup_network_mock
        response = self.app.get(BASE_URL + "/simulation/stop")
        self.assertEqual(200, response.status_code)
        self.assertEqual(b"DONE", response.get_data())
        setup_network_mock.assert_called_once()

    def test_stopSimulationWhenNs3IsNotRunning(self):
        setup_network_mock = Mock(return_value=None)
        self.mock_libvirt_service.setup_all_networks = setup_network_mock
        response = self.app.get(BASE_URL + "/simulation/stop")
        self.assertEqual(200, response.status_code)
        setup_network_mock.assert_called_once()

    # helper
    def register_device(self, device):
        response = self.app.post(BASE_URL + "/register",
                                 data=json.dumps(device),
                                 content_type="application/json")
