from network_simulator.exceptions.device_exceptions import DeviceAlreadyRegisteredException, UnknownDeviceException


class Device:
    def __init__(self, device_data):
        self.device_id = device_data["device_id"]
        self.device_type = device_data["device_type"]
        self.tap_if_name = device_data["tap_if_name"]
        self.xpos = None
        self.ypos = None


class NetworkSimulatorService:
    def __init__(self, net_namespace_name):
        self.net_namespace_name = net_namespace_name
        self.devices = {}

    def register_new_device(self, device_data):
        device_id = device_data["device_id"]
        if device_id in self.devices.keys():
            raise DeviceAlreadyRegisteredException("Cannot add device with ID '{}'. "
                                                   "Device already registered".format(device_id))
        self.devices[device_id] = Device(device_data)
        return self.net_namespace_name

    def unregister_device(self, device_id):
        if device_id not in self.devices.keys():
            raise UnknownDeviceException("Cannot unregister device '{}'.".format(device_id))
        self.devices.pop(device_id)

    def update_devices(self, device_list):
        for device in device_list:
            self.set_device_position(device)

    def set_device_position(self, data_dict):
        device = self.get_device(data_dict["device_id"])
        self.set_device_pos(device, "xpos", data_dict["xpos"])
        self.set_device_pos(device, "ypos", data_dict["ypos"])

    def get_device(self, device_id):
        if device_id in self.devices.keys():
            return self.devices[device_id]
        raise UnknownDeviceException("Cannot get device from stored devices. Device ID '{}' is unknown."
                                     .format(device_id))

    def set_device_pos(self, device, pos, pos_value):
        setattr(device, pos, pos_value)


