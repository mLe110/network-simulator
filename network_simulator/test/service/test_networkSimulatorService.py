from unittest import TestCase
from unittest.mock import patch, mock_open, call

from network_simulator.exceptions.device_exceptions import DeviceAlreadyRegisteredException, UnknownDeviceException
from network_simulator.service import NetworkSimulatorService
from network_simulator.service.network_simulator_service import Device


class TestNetworkSimulatorService(TestCase):
    def setUp(self):
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
        device.xpos = 4.0
        device.ypos = 3.0
        str_rep = "{},{},{},{},{}".format(self.device_id, self.device_type, self.tap_if_name, 4.0, 3.0)
        self.assertEqual(str_rep, str(device))

    def test_writeDeviceConfig(self):
        device1 = self.create_device("test1")
        device2 = self.create_device("test2")
        self.network_svc.devices[device1.device_id] = device1
        self.network_svc.devices[device2.device_id] = device2
        with patch("network_simulator.service.network_simulator_service.open", mock_open()) as mocked_file:
            self.network_svc.write_device_config()
            self.assertEqual([call(str(device1)), call(str(device2))], mocked_file().write.call_args_list)

    def test_registerDeviceTwice(self):
        self.network_svc.devices[self.device_id] = ""
        with self.assertRaises(DeviceAlreadyRegisteredException):
            self.network_svc.register_new_device(self.device_data_dict)

    def test_registerNewDevice(self):
        self.network_svc.register_new_device(self.device_data_dict)
        self.assertIn(self.device_id, self.network_svc.devices.keys())

    def test_unregisterDevice(self):
        self.network_svc.devices[self.device_id] = ""
        self.network_svc.unregister_device(self.device_id)
        self.assertNotIn(self.device_id, self.network_svc.devices.keys())

    def test_unregisterInvalidDevice(self):
        with self.assertRaises(UnknownDeviceException):
            self.network_svc.unregister_device(self.device_id)

    def test_addDeviceXPosition(self):
        self.network_svc.register_new_device(self.device_data_dict)
        self.network_svc.set_device_position(self.device_data_dict)
        self.assertEqual(self.device_data_dict["xpos"], self.network_svc.devices[self.device_id].xpos)

    def test_addDeviceYPosition(self):
        self.network_svc.register_new_device(self.device_data_dict)
        self.network_svc.set_device_position(self.device_data_dict)
        self.assertEqual(self.device_data_dict["ypos"], self.network_svc.devices[self.device_id].ypos)

    # helper
    def create_device(self, device_id):
        device = Device(self.device_data_dict)
        device.device_id = device_id
        device.xpos = 4.0
        device.ypos = 3.0
        return device



