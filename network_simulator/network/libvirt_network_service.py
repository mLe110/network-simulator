import logging

import libvirt

from network_simulator.exceptions.libvirt_network_service_exception import DuplicateNetworkNameException, \
    LibvirtNetworkCreationException, UnknownNetworkException

xml_network_config = """
<network>
  <name>{network_name}</name>
  <bridge name="{network_name}"/>
  <forward mode="nat" />
  <ip address="{bridge_ip}" netmask="{netmask}">
    <dhcp>
        <range start="{start_ip}" end="{end_ip}"/>
    </dhcp>
  </ip>
</network>"""


class NetworkInfo:
    def __init__(self, network_name, gateway_ip, netmask, start_ip, end_ip):
        self.network_name = network_name
        self.gateway_ip = gateway_ip
        self.netmask = netmask
        self.start_ip = start_ip
        self.end_ip = end_ip

    @classmethod
    def from_network_dict(cls, network_dict):
        return cls(network_dict["network_name"], network_dict["gateway_ip"],
                   network_dict["netmask"], network_dict["start_ip"], network_dict["end_ip"])


class LibvirtNetworkService:
    def __init__(self, hypervisor_uri):
        self.logger = logging.getLogger(__name__)
        self.hypervisor_uri = hypervisor_uri
        self.conn = None
        self.network_dict = {}

    def setup_all_networks(self):
        for network_info in self.network_dict.values():
            self.setup_single_network(network_info)

    def setup_new_network(self, network_json):
        network_info = self.add_network(network_json)
        self.setup_single_network(network_info)

    def shutdown_all_networks(self):
        for network_name in self.network_dict.keys():
            self.shutdown_libvirt_network(network_name)

    def shutdown_and_remove_network(self, network_name):
        self.shutdown_libvirt_network(network_name)
        self.remove_network(network_name)

    def shutdown_libvirt_network(self, network_name):
        network = self.get_libvirt_network(network_name)
        network.destroy()

    def get_libvirt_network(self, network_name):
        conn = self.get_hypervisor_connection()
        network = conn.networkLookupByName(network_name)
        if not network:
            self.logger.error("Unable to find network '{}'.".format(network_name))
            raise UnknownNetworkException("Unable to find network '{}'.".format(network_name))
        return network

    def add_network(self, network_json):
        network_info = NetworkInfo.from_network_dict(network_json)
        if network_info.network_name in self.network_dict.keys():
            raise DuplicateNetworkNameException("Network '{}' already exists."
                                                .format(network_info.network_name))

        self.network_dict[network_info.network_name] = network_info
        return network_info

    def remove_network(self, network_name):
        del self.network_dict[network_name]

    def setup_single_network(self, network_info):
        network_config_str = self.create_libvirt_config_str(network_info)
        self.create_libvirt_network(network_config_str)

    def create_libvirt_config_str(self, network_info):
        config_str = xml_network_config.replace("{network_name}", network_info.network_name)
        config_str = config_str.replace("{bridge_ip}", network_info.gateway_ip)
        config_str = config_str.replace("{netmask}", network_info.netmask)
        config_str = config_str.replace("{start_ip}", network_info.start_ip)
        return config_str.replace("{end_ip}", network_info.end_ip)

    def create_libvirt_network(self, network_config_str):
        # create a transient virtual network
        conn = self.get_hypervisor_connection()
        network = conn.networkCreateXML(network_config_str)
        if not network:
            self.logger.error("Failed to define virtual network.")
            raise LibvirtNetworkCreationException("Unable to create virtual network")

        return network

    def get_hypervisor_connection(self):
        if self.conn:
            return self.conn
        else:
            conn = libvirt.open(self.hypervisor_uri)
            if not conn:
                print("Failed to open connection to '{}'.".format(self.hypervisor_uri))
                exit(1)
            return conn
