from werkzeug.exceptions import BadRequest


class InvalidDeviceTypeException(BadRequest):
    """ Exception raised when a device in the submitted has an invalid type, e.g.
    for a valid VIoTD, the JSON contains type "router".
    """

    def __init__(self, msg):
        super().__init__(msg)


class InvalidNetworkTopologyException(BadRequest):
    """ Exception raised when a device in the submitted has an invalid type, e.g.
    for a valid VIoTD, the JSON contains type "router".
    """

    def __init__(self, msg):
        super().__init__(msg)
