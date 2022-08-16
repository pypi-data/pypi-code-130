import json


def is_json_serializable(x):
    """
    Checks if input x is JSON-serializable, returns bool
    """
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


class EvaluationException(Exception):
    """ 
    Exception to be used to return richer errors from evaluaton functions

    Provides a default `message` if not provided as keyword argument
    Allows adding any kwargs, which get passed onto the `error_dict` which
    is returned in the lambda function's response
    """
    default_msg = "An EvaluationException was raised when executing the evaluation function"

    def __init__(self, message=default_msg, **kwargs):
        self.message = message
        self.extra_args = kwargs
        super().__init__(self.message)

    @property
    def error_dict(self):
        """ 
        Packaged input args into an JSON-serializable dict, to be returned under 
        the "error" field in the function's response
        """

        out_args = {
            k: v if is_json_serializable(v) else repr(v)
            for k, v in self.extra_args.items()
        }

        serialization_errors = [
            k for k, v in self.extra_args.items()
            if not is_json_serializable(v)
        ]

        if serialization_errors:
            out_args["serialization_errors"] = serialization_errors

        return {
            "message": self.message,
            **out_args,
        }

    def __repr__(self):
        return self.message

    def __str__(self):
        return json.dumps(self.error_dict, indent=2)
