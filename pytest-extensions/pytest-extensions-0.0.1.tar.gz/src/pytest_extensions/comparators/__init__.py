
class BaseComparator:
    def __init__(self, display=None):
        self.display = display

    def __eq__(self, other):
        return NotImplemented

    def __repr__(self):
        return self.display


class FuncComparator(BaseComparator):
    def __init__(self, func, display=None):
        super(FuncComparator, self).__init__(display=display)

        self.func = func

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        return self

    def __eq__(self, other):
        return self.func(other, *self.args, **self.kwargs)

    def __repr__(self):
        params = ", ".join(list(map(repr, self.args)))
        if self.kwargs:
            params += ", " + ", ".join(f"{k}={repr(v)}" for k, v in self.kwargs.items())

        return f"An object that {self.func.__name__}({params})"
