import json
from unittest.mock import patch

from network_simulator.test.controller.base_api import TestBaseApi, BASE_URL


class TestViotdApi(TestBaseApi):
    @patch("network_simulator.service.network_topology_handler.write_network_topology_to_file")
    def setUp(self, write_network_topology_to_file_mock):
        super().setUp()

    def test_registerDevice(self):
        response = self.app.post(BASE_URL + "/register",
                                 data=json.dumps(self.register_payload),
                                 content_type="application/json")
        data = json.loads(response.get_data())
        self.assertEqual(self.net_namespace_name, data["ns_namespace"])

    def test_registerDeviceTwice(self):
        self.app.post(BASE_URL + "/register",
                                 data=json.dumps(self.register_payload),
                                 content_type="application/json")

        response = self.app.post(BASE_URL + "/register",
                                 data=json.dumps(self.register_payload),
                                 content_type="application/json")
        self.assertEqual(400, response.status_code)

    def test_deregisterDevice(self):
        self.app.post(BASE_URL + "/register",
                                 data=json.dumps(self.register_payload),
                                 content_type="application/json")

        response = self.app.delete(BASE_URL + "/deregister/" + self.device_id)
        self.assertEqual(200, response.status_code)

    def test_deregisterUnknownDevice(self):
        response = self.app.delete(BASE_URL + "/deregister/" + self.device_id)
        self.assertEqual(400, response.status_code)

    def test_invalidPayloadVariableWriting(self):
        del self.register_payload["device_id"]
        self.register_payload["device-id"] = "testId"

        response = self.app.post(BASE_URL + "/register",
                                 data=json.dumps(self.register_payload),
                                 content_type="application/json")

        self.assertEqual(400, response.status_code)


