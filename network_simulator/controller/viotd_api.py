import enum

from flask import (
    Blueprint, request, current_app,
    jsonify)

from network_simulator.exceptions.device_exceptions import DeviceException

viotd_api_bp = Blueprint("viotd_api", __name__)


class ReturnValues(enum.Enum):
    SUCCESS = "DONE"


@viotd_api_bp.route("/")
def endpoints():
    return "possible routes: <br/>" \
           "POST: /register # (with device ID and tap if name)<br/>" \
           "DELETE: /unregister/<device_id>"


@viotd_api_bp.route("/register", methods=["POST"])
def register_device():
    data = request.get_json()
    current_app.logger.debug("Register endpoint called with data: '{}'.".format(data))
    current_app.net_sim_service.register_new_device(data["device_id"])
    return ReturnValues.SUCCESS.value


@viotd_api_bp.route("/unregister/<device_id>", methods=["DELETE"])
def unregister_device(device_id):
    current_app.logger.debug("Unregister endpoint called with data: '{}'.".format(device_id))
    current_app.net_sim_service.unregister_device(device_id)
    return ReturnValues.SUCCESS.value


# implement error handler
@viotd_api_bp.errorhandler(404)
def no_endpoint(error):
    current_app.logger.warning("Unknown endpoint called")
    return "Unknown endpoint."


@viotd_api_bp.errorhandler(DeviceException)
def exception_wrapper(ex):
    response = {
        "error": {
            "type": ex.__class__.__name__,
            "message": str(ex.args[1])
        }
    }
    return jsonify(response), 400
