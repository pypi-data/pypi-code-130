import warnings


class _Agent:
    def __init__(self, init_state):
        self.init_state = init_state
        self.current_state = init_state

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key == "init_state":
                if type(value) == tuple or len(value) == self.init_state:
                    self.init_state = value
                else:
                    msg = "Unable to update attribute 'init_state', unsupported type or length, ignored"
                    warnings.warn(msg)
            elif key == "current_state":
                if type(value) == tuple or len(value) == self.current_state:
                    self.current_state = value
                else:
                    msg = "Unable to update attribute 'current_state', unsupported type or length, ignored"
                    warnings.warn(msg)
            else:
                msg = "'Agent' object don't have attribute '{}', ignored.".format(key)
                warnings.warn(msg)

    def reset(self):
        self.current_state = self.init_state

    def __repr__(self):
        return "Agent(current_state={}, init_state={})".format(
            self.current_state,
            self.init_state
        )
