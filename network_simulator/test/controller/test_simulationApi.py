import json

from network_simulator.test.controller.base_api import TestBaseApi, BASE_URL


class TestViotdApi(TestBaseApi):
    def setUp(self):
        super().setUp()
        self.device1 = {"device_id": "test1", "device_type": "vm", "tap_if_name": "tap1"}
        self.device2 = {"device_id": "test2", "device_type": "container", "tap_if_name": "tap2"}
        self.devices_list = [{"device_id": "test1", "xpos": 1, "ypos": 2},
                             {"device_id": "test2", "xpos": 2, "ypos": 1}]

    def test_startSimulationWithNoDevices(self):
        response = self.app.post(BASE_URL + "/simulate",
                                 data=json.dumps([]),
                                 content_type="application/json")
        self.assertEqual(400, response.status_code)

    def test_startSimulationWithUnknownDevices(self):
        self.devices_list.append({"device_id": "invalid", "xpos": 4, "ypos": 5})
        response = self.app.post(BASE_URL + "/simulate",
                                 data=json.dumps(self.devices_list),
                                 content_type="application/json")
        self.assertEqual(400, response.status_code)

    def test_startSimulationWithNone(self):
        response = self.app.post(BASE_URL + "/simulate",
                                 data=json.dumps(None),
                                 content_type="application/json")
        self.assertEqual(400, response.status_code)

    def test_startSimulationWithTwoDevices(self):
        self.register_device(self.device1)
        self.register_device(self.device2)
        response = self.app.post(BASE_URL + "/simulate",
                                 data=json.dumps(self.devices_list),
                                 content_type="application/json")
        self.assertEqual(200, response.status_code)
        self.assertEqual(b"DONE", response.get_data())

    # helper
    def register_device(self, device):
        response = self.app.post(BASE_URL + "/register",
                                 data=json.dumps(device),
                                 content_type="application/json")
