from unittest import TestCase

from network_simulator import create_app

BASE_URL = "http://127.0.0.1:5000/api/v1"


class TestBaseApi(TestCase):
    def setUp(self):
        self.device_id = "testdevice"
        self.device_type = "vm"
        self.tap_if_name = "testtap"
        self.net_namespace_name = "testns"
        self.app = create_app(self.net_namespace_name).test_client()
        self.register_payload = {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "tap_if_name": self.tap_if_name,
        }
