import argparse
import os
import docker

docker_client = docker.from_env()
docker_api = docker.APIClient(base_url='unix://var/run/docker.sock')


def run_container(args_config):
    container = docker_client.containers.run(image="mle110/ns:0.1",
                                             name=args_config.ns_container_name,
                                             ports={'5000/tcp': 5000},
                                             environment={
                                                 "HYPERVISOR_URI": args_config.hypervisor_uri
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
    parser.add_argument("--hypervisor-uri", required=True, type=str, help="The URI of the hypervisor libvirt should "
                                                                          "use.")
    args = parser.parse_args()

    setup_network_service_network(args)

