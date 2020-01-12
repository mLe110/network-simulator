import json
from unittest.mock import Mock, patch

from network_simulator.test.controller.base_api import TestBaseApi, BASE_URL


class TestViotdApi(TestBaseApi):
    def setUp(self):
        super().setUp()
        self.app.application.net_sim_service.start_ns3 = Mock(return_value=None)
        self.app.application.net_sim_service.write_device_config = Mock(return_value=None)
        self.device1 = {"device_id": "test1", "device_type": "vm", "tap_if_name": "tap1"}
        self.device2 = {"device_id": "test2", "device_type": "container", "tap_if_name": "tap2"}
        self.devices_list = [{"device_id": "test1", "xpos": 1, "ypos": 2},
                             {"device_id": "test2", "xpos": 2, "ypos": 1}]

    def test_startSimulationWithNoDevices(self):
        response = self.app.post(BASE_URL + "/simulation/start",
                                 data=json.dumps([]),
                                 content_type="application/json")
        self.assertEqual(400, response.status_code)

    def test_startSimulationWithUnknownDevices(self):
        self.devices_list.append({"device_id": "invalid", "xpos": 4, "ypos": 5})
        response = self.app.post(BASE_URL + "/simulation/start",
                                 data=json.dumps(self.devices_list),
                                 content_type="application/json")
        self.assertEqual(400, response.status_code)

    def test_startSimulationWithNone(self):
        response = self.app.post(BASE_URL + "/simulation/start",
                                 data=json.dumps(None),
                                 content_type="application/json")
        self.assertEqual(400, response.status_code)

    def test_startSimulationWithTwoDevices(self):
        self.register_device(self.device1)
        self.register_device(self.device2)
        self.app.application.net_sim_service.start_ns3 = Mock(return_value=None)
        response = self.app.post(BASE_URL + "/simulation/start",
                                 data=json.dumps(self.devices_list),
                                 content_type="application/json")
        self.assertEqual(200, response.status_code)
        self.assertEqual(b"DONE", response.get_data())

    @patch("network_simulator.service.network_simulator_service.os")
    def test_stopSimulationWhenNs3Running(self, mock_os):
        self.app.application.net_sim_service.proc = Mock()
        response = self.app.get(BASE_URL + "/simulation/stop")
        self.assertEqual(200, response.status_code)
        self.assertEqual(b"DONE", response.get_data())

    def test_stopSimulationWhenNs3IsNotRunning(self):
        response = self.app.get(BASE_URL + "/simulation/stop")
        self.assertEqual(400, response.status_code)

    # helper
    def register_device(self, device):
        response = self.app.post(BASE_URL + "/register",
                                 data=json.dumps(device),
                                 content_type="application/json")
