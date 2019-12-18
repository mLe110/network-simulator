import json
from unittest import TestCase

from network_simulator import create_app

BASE_URL = "http://127.0.0.1:5000/api/v1"


class TestViotdApi(TestCase):
    def setUp(self):
        self.device_id = "testdevice"
        self.net_namespace_name = "testns"
        self.app = create_app(self.net_namespace_name).test_client()
        self.register_payload = {"device_id": self.device_id}

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

    def test_unregisterDevice(self):
        self.app.post(BASE_URL + "/register",
                                 data=json.dumps(self.register_payload),
                                 content_type="application/json")

        response = self.app.delete(BASE_URL + "/unregister/" + self.device_id)
        self.assertEqual(200, response.status_code)

    def test_unregisterUnknownDevice(self):
        response = self.app.delete(BASE_URL + "/unregister/" + self.device_id)
        self.assertEqual(400, response.status_code)
