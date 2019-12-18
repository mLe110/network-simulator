class DeviceException(Exception):
    """ General exception for device. Every device exception should inherit this class.
    """

    def __init__(self, msg):
        super().__init__(self, msg)


class DeviceAlreadyRegisteredException(DeviceException):
    """ Exception raised when a device was already registered.
    """

    def __init__(self, msg):
        super().__init__(msg)


class UnknownDeviceException(DeviceException):
    """ Exception raised when a device is not known to the service.
    """

    def __init__(self, msg):
        super().__init__(msg)
