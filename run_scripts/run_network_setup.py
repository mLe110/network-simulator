import argparse
import os
import libvirt
import docker

xml_bridge_config = """
<network>
  <name>{network_name}</name>
  <forward mode="nat" />
  <ip address="{bridge_ip}" netmask="{netmask}">
    <dhcp>
        <range start="{start_ip}" end="{end_ip}"/>
    </dhcp>
  </ip>
</network>"""

docker_client = docker.from_env()
docker_api = docker.APIClient(base_url='unix://var/run/docker.sock')


def create_libvirt_config_str(args_config):
    config_str = xml_bridge_config.replace("{network_name}", args_config.libvirt_network_name)
    config_str = config_str.replace("{bridge_ip}", args_config.libvirt_bridge_ip)
    config_str = config_str.replace("{netmask}", args_config.libvirt_netmask)
    config_str = config_str.replace("{start_ip}", args_config.libvirt_start_ip)
    return config_str.replace("{end_ip}", args_config.libvirt_end_ip)


def get_hypervisor_connection(hypervisor_uri):
    conn = libvirt.open(hypervisor_uri)
    if not conn:
        print("Failed to open connection to '{}'.".format(hypervisor_uri))
        exit(1)
    return conn


def create_libvirt_network(conn, network_config_str):
    # create a transient virtual network
    network = conn.networkCreateXML(network_config_str)
    if not network:
        print("Failed to define a virtual network.")
        exit(1)


def setup_libvirt_network(args_config):
    libvirt_config_str = create_libvirt_config_str(args_config)
    conn = get_hypervisor_connection(args_config.hypervisor_uri)
    create_libvirt_network(conn, libvirt_config_str)
    conn.close()


def run_container(args_config):
    container = docker_client.containers.run(image="mle110/ns:0.1",
                                             name=args_config.ns_container_name,
                                             ports={'5000/tcp': 5000},
                                             environment={
                                                 "IP_BASE": args_config.ns3_ip_subnet,
                                                 "IP_NETMASK": args_config.ns3_ip_netmask,
                                             },
                                             volumes={"/var/run/netns": {
                                                 "bind": "/var/run/netns",
                                             }},
                                             cap_add=["NET_ADMIN"],
                                             devices=["/dev/net/tun:/dev/net/tun"],
                                             detach=True,
                                             remove=True)
    return container.id[:12]


def get_container_pid(container_id):
    return docker_api.inspect_container(container_id)["State"]["Pid"]


def mount_container_net_namespace(container_id):
    pid = get_container_pid(container_id)
    os.symlink("/proc/" + str(pid) + "/ns/net",
               "/var/run/netns/" + container_id)


def close_docker_clients():
    docker_api.close()
    docker_client.close()


def setup_network_service_network(args_config):
    container_id = run_container(args_config)
    mount_container_net_namespace(container_id)
    close_docker_clients()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ns-container-name", required=True, type=str, help="The name the network service container "
                                                                             "should have.")
    parser.add_argument("--ns3-ip-subnet", required=True, type=str, help="The IP subnet used in the ns3 simulation.")
    parser.add_argument("--ns3-ip-netmask", required=True, type=str,
                        help="The netmask for the IP subnet used in the ns3 simulation.")
    parser.add_argument("--hypervisor-uri", required=True, type=str, help="The URI of the hypervisor libvirt should "
                                                                          "use.")
    parser.add_argument("--libvirt-network-name", required=True, type=str, help="The name of the libvirt network "
                                                                                "which will be created.")
    parser.add_argument("--libvirt-bridge-ip", required=True, type=str, help="The IP of the bridge for the libvirt "
                                                                             "network.")
    parser.add_argument("--libvirt-start-ip", required=True, type=str, help="The start IP of the used IP range for "
                                                                            "the libvirt network.")
    parser.add_argument("--libvirt-end-ip", required=True, type=str, help="The end IP of the used IP range for "
                                                                          "the libvirt network.")
    parser.add_argument("--libvirt-netmask", required=True, type=str, help="The netmask used by the libvirt network.")
    args = parser.parse_args()

    setup_libvirt_network(args)
    setup_network_service_network(args)

