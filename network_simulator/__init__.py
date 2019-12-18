from flask import Flask

from network_simulator.service import register_network_simulator_service


def create_app(net_namespace_name, config=None):
    # create flask application
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    register_network_simulator_service(app, net_namespace_name)

    # apply blueprints to app
    from network_simulator.controller import viotd_api, simulation_api
    app.register_blueprint(viotd_api.viotd_api_bp, url_prefix="/api/v1")
    app.register_blueprint(simulation_api.simulation_api_bp, url_prefix="/api/v1")

    return app

