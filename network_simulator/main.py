import argparse
import logging
import platform

from network_simulator import create_app


def get_container_id():
    return platform.node()


def setup_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s - %(levelname)s - %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        filename="network_simulator.log",
                        filemode="w")


if __name__ == "__main__":
    setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("--sim-ip-subnet", required=True, type=str, help="The IP subnet used in the simulation.")
    args = parser.parse_args()

    net_namespace = get_container_id()
    app = create_app(net_namespace)

    app.run()
