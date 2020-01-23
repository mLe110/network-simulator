import logging
import os
import signal
import subprocess
import threading

from network_simulator.exceptions.device_exceptions import DeviceAlreadyRegisteredException, UnknownDeviceException
from network_simulator.exceptions.network_simulator_service_exception import SimulationException
from network_simulator.service.network_topology_handler import process_network_topology


class Device:
    def __init__(self, device_data):
        self.device_id = device_data["device_id"]
        self.device_type = device_data["device_type"]
        self.tap_if_name = device_data["tap_if_name"]

    def __str__(self):
        return "{},{},{}".format(self.device_id, self.device_type,
                                 self.tap_if_name)


class NetworkSimulatorService:
    def __init__(self, net_namespace_name):
        self.logger = logging.getLogger(__name__)
        self.device_config_file_path = "/app/network_topology.json"
        self.sim_src_file = "network-template-core"
        self.net_namespace_name = net_namespace_name
        self.proc = None
        self.devices = {}

    def register_new_device(self, device_data):
        device_id = device_data["device_id"]
        if device_id in self.devices.keys():
            raise DeviceAlreadyRegisteredException("Cannot add device with ID '{}'. "
                                                   "Device already registered".format(device_id))
        self.logger.info("Register new device with ID {}.".format(device_id))
        self.devices[device_id] = Device(device_data)
        return self.net_namespace_name

    def deregister_device(self, device_id):
        if device_id not in self.devices.keys():
            raise UnknownDeviceException("Cannot deregister device '{}'.".format(device_id))
        self.logger.info("Deregister device with ID {}.".format(device_id))
        self.devices.pop(device_id)

    def run_simulation(self, network_topology_json):
        self.logger.info("Run simulation.")
        process_network_topology(self.devices, self.device_config_file_path,
                                 network_topology_json)
        self.start_ns3(self.sim_src_file)

    def stop_simulation(self):
        self.logger.info("Stop simulation.")
        if self.proc:
            os.killpg(os.getpgid(self.proc.pid), signal.SIGINT)
        else:
            raise SimulationException("Cannot stop simulation. Simulation not running.")

    def start_ns3(self, sim_src_file):
        self.logger.debug("Start simulation with simulation file '{}'.".format(sim_src_file))
        self.proc = subprocess.Popen(["$WAF --run " + sim_src_file], stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, shell=True, preexec_fn=os.setsid)
        th = threading.Thread(target=self.output_reader, daemon=True)
        th.start()

    def output_reader(self):
        self.logger.debug("Start thread for logging ns-3 output.")
        for line in iter(self.proc.stdout.readline, b''):
            self.logger.info(line.decode("utf-8"))
