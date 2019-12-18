import argparse
import platform

from network_simulator import create_app


def get_container_id():
    return platform.node()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sim-ip-subnet", required=True, type=str, help="The IP subnet used in the simulation.")
    args = parser.parse_args()

    net_namespace = get_container_id()
    app = create_app(net_namespace)

    app.run()
