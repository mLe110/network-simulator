from werkzeug.exceptions import BadRequest


class SimulationException(BadRequest):
    """ Exception raised when a error occurs with handling ns-3.
    """

    def __init__(self, msg):
        super().__init__(msg)
