import json
from unittest.mock import Mock

from network_simulator.test.controller.base_api import TestBaseApi, BASE_URL


class TestViotdApi(TestBaseApi):
    def setUp(self):
        super().setUp()
        self.network_info_json = {
            "network_name": "testnet",
            "gateway_ip": "10.1.1.1",
            "netmask": "255.255.255.0",
            "start_ip": "10.1.1.40",
            "end_ip": "10.1.1.50"
        }
        self.mock_conn = Mock()
        self.mock_conn.create_libvirt_network.return_value = Mock()
        self.app.application.libvirt_network_service.get_hypervisor_connection = Mock(return_value=self.mock_conn)

    def test_createNewNetwork(self):
        response = self.app.post(BASE_URL + "/network/create",
                                data=json.dumps(self.network_info_json),
                                content_type="application/json")
        self.assertEqual(200, response.status_code)

    def test_createNetworkTwice(self):
        response = self.app.post(BASE_URL + "/network/create",
                                 data=json.dumps(self.network_info_json),
                                 content_type="application/json")
        self.assertEqual(200, response.status_code)
        response = self.app.post(BASE_URL + "/network/create",
                                 data=json.dumps(self.network_info_json),
                                 content_type="application/json")
        self.assertEqual(400, response.status_code)

    def test_removeNetwork(self):
        self.app.post(BASE_URL + "/network/create",
                                 data=json.dumps(self.network_info_json),
                                 content_type="application/json")
        response = self.app.delete(BASE_URL + "/network/remove/" + self.network_info_json["network_name"])
        self.assertEqual(200, response.status_code)

    def test_removeUnknownNetwork(self):
        response = self.app.delete(BASE_URL + "/network/remove/" + self.network_info_json["network_name"])
        self.assertEqual(400, response.status_code)
