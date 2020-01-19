from unittest import TestCase
from unittest.mock import patch, mock_open, call

from network_simulator.exceptions.device_exceptions import DeviceAlreadyRegisteredException, UnknownDeviceException
from network_simulator.service import NetworkSimulatorService
from network_simulator.service.network_simulator_service import Device


class TestNetworkSimulatorService(TestCase):
    @patch("network_simulator.service.network_topology_handler.write_network_topology_to_file")
    def setUp(self, write_network_topology_to_file_mock):
        self.device_id = "testid"
        self.device_type = "vm"
        self.tap_if_name = "testtap"
        self.device_data_dict = {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "tap_if_name": self.tap_if_name,
            "xpos": 5.0,
            "ypos": 3.0
        }
        self.test_net_namespace = "testns"
        self.network_svc = NetworkSimulatorService(self.test_net_namespace)

    def test_deviceStrRepresentation(self):
        device = Device(self.device_data_dict)
        str_rep = "{},{},{}".format(self.device_id, self.device_type, self.tap_if_name)
        self.assertEqual(str_rep, str(device))

    def test_registerDeviceTwice(self):
        self.network_svc.devices[self.device_id] = ""
        with self.assertRaises(DeviceAlreadyRegisteredException):
            self.network_svc.register_new_device(self.device_data_dict)

    def test_registerNewDevice(self):
        self.network_svc.register_new_device(self.device_data_dict)
        self.assertIn(self.device_id, self.network_svc.devices.keys())

    def test_deregisterDevice(self):
        self.network_svc.devices[self.device_id] = ""
        self.network_svc.deregister_device(self.device_id)
        self.assertNotIn(self.device_id, self.network_svc.devices.keys())

    def test_deregisterInvalidDevice(self):
        with self.assertRaises(UnknownDeviceException):
            self.network_svc.deregister_device(self.device_id)

    # helper
    def create_device(self, device_id):
        device = Device(self.device_data_dict)
        device.device_id = device_id
        device.xpos = 4.0
        device.ypos = 3.0
        return device



