from flask import (
    Blueprint, request, current_app,
    jsonify)
from werkzeug.exceptions import BadRequest

from network_simulator.controller.return_value import ReturnValues
from network_simulator.exceptions.network_simulator_service_exception import SimulationException
from network_simulator.exceptions.network_topology_handler_exception import InvalidNetworkTopologyException

simulation_api_bp = Blueprint("simulation_api", __name__)


@simulation_api_bp.route("/start", methods=["POST"])
def run_simulation():
    network_topology_json = request.get_json()
    if network_topology_json:
        current_app.libvirt_network_service.shutdown_all_networks()
        current_app.net_sim_service.run_simulation(network_topology_json)
        return ReturnValues.SUCCESS.value
    else:
        raise InvalidNetworkTopologyException("Simulation cannot be started "
                                              "when network topology is None.")


@simulation_api_bp.route("/stop", methods=["GET"])
def stop_simulation():
    current_app.libvirt_network_service.setup_all_networks()
    try:
        current_app.net_sim_service.stop_simulation()
    except SimulationException as ex:
        current_app.logger.warning("Error while stopping simulation: '{}'.".format(ex.description))
    return ReturnValues.SUCCESS.value


@simulation_api_bp.errorhandler(BadRequest)
def exception_wrapper(ex):
    response = {
        "error": {
            "type": ex.__class__.__name__,
            "message": str(ex.description)
        }
    }
    return jsonify(response), 400
