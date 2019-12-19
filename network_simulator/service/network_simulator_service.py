import subprocess

from network_simulator.exceptions.device_exceptions import DeviceAlreadyRegisteredException, UnknownDeviceException
from network_simulator.exceptions.network_simulator_service_exception import SimulationException


class Device:
    def __init__(self, device_data):
        self.device_id = device_data["device_id"]
        self.device_type = device_data["device_type"]
        self.tap_if_name = device_data["tap_if_name"]
        self.xpos = None
        self.ypos = None

    def __str__(self):
        return "{},{},{},{},{}".format(self.device_id, self.device_type,
                                       self.tap_if_name, self.xpos, self.ypos)


class NetworkSimulatorService:
    def __init__(self, net_namespace_name):
        self.device_config_file_path = "sim_devices.conf"
        self.net_namespace_name = net_namespace_name
        self.proc = None
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

    def run_simulation(self, device_list):
        self.update_devices(device_list)
        self.write_device_config()
        # TODO make simulation source file configurable
        sim_src_file = "tap-wifi-full_setup"
        self.start_ns3(sim_src_file)

    def stop_simulation(self):
        if self.proc:
            pass
        else:
            raise SimulationException("Cannot stop simulation. Simulation not running.")

    def update_devices(self, device_list):
        for device in device_list:
            self.set_device_position(device)

    def write_device_config(self):
        with open(self.device_config_file_path, "w") as f:
            for device in self.devices.values():
                f.write(str(device) + '\n')

    def start_ns3(self, sim_src_file):
        self.proc = subprocess.Popen(["$WAF", "--run", sim_src_file], shell=True)

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


