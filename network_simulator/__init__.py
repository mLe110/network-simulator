from flask import Flask

from network_simulator.network import register_libvirt_network_service
from network_simulator.service import register_network_simulator_service


def create_app(net_namespace_name, config=None):
    # create flask application
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    register_network_simulator_service(app, net_namespace_name)
    register_libvirt_network_service(app)

    # apply blueprints to app
    from network_simulator.controller import viotd_api, simulation_api, libvirt_network_api
    app.register_blueprint(viotd_api.viotd_api_bp, url_prefix="/api/v1")
    app.register_blueprint(simulation_api.simulation_api_bp, url_prefix="/api/v1/simulation")
    app.register_blueprint(libvirt_network_api.libvirt_network_api_bp, url_prefix="/api/v1/network")

    return app
