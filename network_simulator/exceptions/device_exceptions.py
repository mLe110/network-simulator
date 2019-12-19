from werkzeug.exceptions import BadRequest


class DeviceAlreadyRegisteredException(BadRequest):
    """ Exception raised when a device was already registered.
    """

    def __init__(self, msg):
        super().__init__(msg)


class UnknownDeviceException(BadRequest):
    """ Exception raised when a device is not known to the service.
    """

    def __init__(self, msg):
        super().__init__(msg)


class InvalidDeviceListException(BadRequest):
    """ Exception raised when device list sent for simulation is invalid.
    """

    def __init__(self, msg):
        super().__init__(msg)
