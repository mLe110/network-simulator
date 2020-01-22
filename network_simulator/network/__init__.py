import os

from network_simulator.network.libvirt_network_service import LibvirtNetworkService


def register_libvirt_network_service(app):
    hypvervisor_uri = os.getenv("HYPERVISOR_URI")
    libvirt_svc = LibvirtNetworkService(hypvervisor_uri)
    setattr(app, "libvirt_network_service", libvirt_svc)
