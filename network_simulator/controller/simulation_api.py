from flask import (
    Blueprint, request, current_app,
    jsonify)
from werkzeug.exceptions import BadRequest

from network_simulator.controller.return_value import ReturnValues
from network_simulator.exceptions.device_exceptions import InvalidDeviceListException

simulation_api_bp = Blueprint("simulation_api", __name__)


@simulation_api_bp.route("/start", methods=["POST"])
def run_simulation():
    devices_list = request.get_json()
    if devices_list and len(devices_list) > 1:
        current_app.net_sim_service.run_simulation(devices_list)
        return ReturnValues.SUCCESS.value
    else:
        raise InvalidDeviceListException("Simulation cannot be started with '{}' devices."
                                         .format(devices_list))


@simulation_api_bp.route("/stop", methods=["GET"])
def stop_simulation():
    current_app.net_sim_service.stop_simulation()
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
