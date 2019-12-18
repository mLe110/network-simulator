from network_simulator.service.network_simulator_service import NetworkSimulatorService


def register_network_simulator_service(app, net_namespace_name):
    net_sim_service = NetworkSimulatorService(net_namespace_name)
    setattr(app, "net_sim_service", net_sim_service)
