class Event:
    def _get_name(self) -> str:
        return self.__class__.__name__
