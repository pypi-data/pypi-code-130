def auth_required(func):
    def function(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception:
            self.auth()
            return func(self, *args, **kwargs)

    return function
