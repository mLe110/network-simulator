from flask import (
    Blueprint, request, current_app,
    jsonify)
from werkzeug.exceptions import BadRequest

from network_simulator.controller.return_value import ReturnValues

viotd_api_bp = Blueprint("viotd_api", __name__)


@viotd_api_bp.route("/register", methods=["POST"])
def register_device():
    data = request.get_json()
    current_app.logger.debug("Register endpoint called with data: '{}'.".format(data))
    net_ns = current_app.net_sim_service.register_new_device(data)
    return jsonify({
        "ns_namespace": net_ns
    })


@viotd_api_bp.route("/deregister/<device_id>", methods=["DELETE"])
def deregister_device(device_id):
    current_app.logger.debug("Deregister endpoint called with data: '{}'.".format(device_id))
    current_app.net_sim_service.deregister_device(device_id)
    return ReturnValues.SUCCESS.value


# implement error handler
@viotd_api_bp.errorhandler(404)
def no_endpoint(error):
    current_app.logger.warning("Unknown endpoint called")
    return "Unknown endpoint."


@viotd_api_bp.errorhandler(KeyError)
@viotd_api_bp.errorhandler(BadRequest)
def exception_wrapper(ex):
    response = {
        "error": {
            "type": ex.__class__.__name__,
            "message":  str(ex.description) if hasattr(ex, "description") else str(ex)
        }
    }
    return jsonify(response), 400
