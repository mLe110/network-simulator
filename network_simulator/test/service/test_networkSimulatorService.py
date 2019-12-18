from unittest import TestCase

from network_simulator.exceptions.device_exceptions import DeviceAlreadyRegisteredException, UnknownDeviceException
from network_simulator.service import NetworkSimulatorService


class TestNetworkSimulatorService(TestCase):
    def setUp(self):
        self.device_id = "testid"
        self.device_data_dict = {
            "device_id": self.device_id,
            "xpos": 5.0,
            "ypos": 3.0
        }
        self.test_net_namespace = "testns"
        self.network_svc = NetworkSimulatorService(self.test_net_namespace)

    def test_registerDeviceTwice(self):
        self.network_svc.devices[self.device_id] = ""
        with self.assertRaises(DeviceAlreadyRegisteredException):
            self.network_svc.register_new_device(self.device_id)

    def test_registerNewDevice(self):
        self.network_svc.register_new_device(self.device_id)
        self.assertIn(self.device_id, self.network_svc.devices.keys())

    def test_unregisterDevice(self):
        self.network_svc.devices[self.device_id] = ""
        self.network_svc.unregister_device(self.device_id)
        self.assertNotIn(self.device_id, self.network_svc.devices.keys())

    def test_unregisterInvalidDevice(self):
        with self.assertRaises(UnknownDeviceException):
            self.network_svc.unregister_device(self.device_id)

    def test_addDeviceXPosition(self):
        self.network_svc.register_new_device(self.device_id)
        self.network_svc.set_device_position(self.device_data_dict)
        self.assertEqual(self.device_data_dict["xpos"], self.network_svc.devices[self.device_id].xpos)

    def test_addDeviceYPosition(self):
        self.network_svc.register_new_device(self.device_id)
        self.network_svc.set_device_position(self.device_data_dict)
        self.assertEqual(self.device_data_dict["ypos"], self.network_svc.devices[self.device_id].ypos)



