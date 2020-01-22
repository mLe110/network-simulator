import argparse
import os
import docker

docker_client = docker.from_env()


def get_container(container_name):
    return docker_client.containers.get(container_name)


def shutdown_network_service_container(container):
    container_id = container.id[:12]
    container.stop()
    return container_id


def unmount_container_net_namespace(container_id):
    os.unlink("/var/run/netns/" + container_id)


def shutdown_network_service_network(container_name):
    container = get_container(container_name)
    container_id = shutdown_network_service_container(container)
    unmount_container_net_namespace(container_id)
    docker_client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ns-container-name", required=True, type=str, help="The name the network service container "
                                                                             "should have.")
    args = parser.parse_args()

    shutdown_network_service_network(args.ns_container_name)
