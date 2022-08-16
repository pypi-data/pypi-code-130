class SlackException(Exception):
    def __init__(self):
        super().__init__(self.message)


class ApiError(SlackException):
    message = "Slack Api error"
