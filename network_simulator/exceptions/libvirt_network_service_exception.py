from werkzeug.exceptions import BadRequest


class DuplicateNetworkNameException(BadRequest):
    """ Exception raised when a libvirt network should be created
    which already exists.
    """

    def __init__(self, msg):
        super().__init__(msg)


class LibvirtHypervisorConnectionException(Exception):
    """ Exception raised when a connection with the hypervisor could
    not be established
    """

    def __init__(self, msg):
        super().__init__(msg)


class LibvirtNetworkCreationException(Exception):
    """ Exception raised when creating a new libvirt network failed.
    """

    def __init__(self, msg):
        super().__init__(msg)


class UnknownNetworkException(BadRequest):
    """ Exception raised when the network is unknown to the network simulator.
    """

    def __init__(self, msg):
        super().__init__(msg)
