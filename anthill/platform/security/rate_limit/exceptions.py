class RateLimitException(Exception):
    """
    Rate limit exception class.
    """

    def __init__(self, state=None, message=''):
        super(RateLimitException, self).__init__(message)
        self.state = state or {}
