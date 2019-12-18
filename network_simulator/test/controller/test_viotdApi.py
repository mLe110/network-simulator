import json

from network_simulator.test.controller.base_api import TestBaseApi, BASE_URL


class TestViotdApi(TestBaseApi):
    def setUp(self):
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

    def test_unregisterDevice(self):
        self.app.post(BASE_URL + "/register",
                                 data=json.dumps(self.register_payload),
                                 content_type="application/json")

        response = self.app.delete(BASE_URL + "/unregister/" + self.device_id)
        self.assertEqual(200, response.status_code)

    def test_unregisterUnknownDevice(self):
        response = self.app.delete(BASE_URL + "/unregister/" + self.device_id)
        self.assertEqual(400, response.status_code)
