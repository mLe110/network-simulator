import argparse
import os
import libvirt
import docker

docker_client = docker.from_env()


def get_hypervisor_connection(hypervisor_uri):
    conn = libvirt.open(hypervisor_uri)
    if not conn:
        print("Failed to open connection to '{}'.".format(hypervisor_uri))
        exit(1)
    return conn


def get_libvirt_network(conn, network_name):
    return conn.networkLookupByName(network_name)


def shutdown_libvirt_network(args_config):
    conn = get_hypervisor_connection(args_config.hypervisor_uri)
    network = get_libvirt_network(conn, args_config.libvirt_network_name)
    network.destroy()
    conn.close()


def get_container(container_name):
    return docker_client.get(container_name)


def shutdown_network_service_container(container):
    container_id = container.id[:12]
    container.stop()
    return container_id


def unmount_container_net_namespace(container_id):
    os.unlink("/var/run/netns/" + container_id)


def setup_network_service_network(container_name):
    container = get_container(container_name)
    container_id = shutdown_network_service_container(container)
    unmount_container_net_namespace(container_id)
    docker_client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ns-container-name", required=True, type=str, help="The name the network service container "
                                                                             "should have.")
    parser.add_argument("--hyperviser-uri", required=True, type=str, help="The URI of the hypervisor libvirt should "
                                                                          "use.")
    parser.add_argument("--libvirt-network-name", required=True, type=str, help="The name of the libvirt network "
                                                                                "which will be created.")
    args = parser.parse_args()

    shutdown_libvirt_network(args)
    setup_network_service_network(args.ns_container_name)
