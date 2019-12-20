import argparse
import logging
import platform

from network_simulator import create_app


def get_container_id():
    return platform.node()


def setup_logging():
    log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    file_handler = logging.FileHandler("network_simulator.log")
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.DEBUG)

    logging.basicConfig(handlers=[file_handler, console_handler])


if __name__ == "__main__":
    setup_logging()
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--sim-ip-subnet", required=True, type=str, help="The IP subnet used in the simulation.")
    # args = parser.parse_args()

    net_namespace = get_container_id()
    app = create_app(net_namespace)

    app.run(debug=True, host="0.0.0.0", port=5000)
