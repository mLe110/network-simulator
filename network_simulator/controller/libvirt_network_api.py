from flask import (
    Blueprint, request, current_app, jsonify)
from werkzeug.exceptions import BadRequest

from network_simulator.controller.return_value import ReturnValues

libvirt_network_api_bp = Blueprint("libvirt_network_api", __name__)


@libvirt_network_api_bp.route("/create", methods=["POST"])
def add_and_create_new_network():
    data = request.get_json()
    current_app.libvirt_network_service.setup_new_network(data)
    return ReturnValues.SUCCESS.value


@libvirt_network_api_bp.route("remove/<network_name>", methods=["DELETE"])
def remove_network(network_name):
    current_app.libvirt_network_service.shutdown_and_remove_network(network_name)
    return ReturnValues.SUCCESS.value


@libvirt_network_api_bp.errorhandler(KeyError)
@libvirt_network_api_bp.errorhandler(BadRequest)
def exception_wrapper(ex):
    response = {
        "error": {
            "type": ex.__class__.__name__,
            "message":  str(ex.description) if hasattr(ex, "description") else str(ex)
        }
    }
    return jsonify(response), 400
