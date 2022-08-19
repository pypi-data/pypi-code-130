class later:
    """
    usage:
        from lambda_ex import later
        ...
        button.on_clicked.connect(delegate := later())

        @delegate.bind
        def foo():
            ...
    """
    func = None

    def __call__(self, *args, **kwargs):
        assert self.func is not None
        return self.func(*args, **kwargs)

    def bind(self, func):
        # TODO: use funcs instead of func to hold multiple targets.
        self.func = func
