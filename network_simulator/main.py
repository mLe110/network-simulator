import argparse

from network_simulator import create_app

# TODO or get net namespace name from cat /proc/self/cgroup

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--net-namespace", required=True, type=str, help="The namespace the container is running in.")
    args = parser.parse_args()

    app = create_app(args.net_namespace)

    app.run()
