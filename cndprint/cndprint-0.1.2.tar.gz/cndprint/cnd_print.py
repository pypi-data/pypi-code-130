from datetime import datetime


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class CndPrint:
    separator = "#|#"
    colors = {
        'e': Bcolors.FAIL,  # Error
        'v': Bcolors.WARNING,  # Event
        'd': Bcolors.OKBLUE,  # display (default)
        's': Bcolors.OKGREEN,  # Success (default)
        'c': Bcolors.OKCYAN,  # Cyan (nothing special, just different color)
    }
    states = ['trace', 'log', 'info']

    def __init__(self, level="Info", uuid=None, silent_mode=False):
        self.level_index = CndPrint.states.index(level.lower())
        self.uuid = uuid
        self.silent_mode = silent_mode
        for state in CndPrint.states:
            for color in CndPrint.colors:
                setattr(CndPrint, f"{state}_{color}", self.make_method("log", color, state))

    def __build_message(self, message):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        uuid = ""
        if self.uuid is not None:
            uuid = "{uuid}{separator}".format(separator=self.separator, uuid=self.uuid)
        full_message = "{uuid}{date}{separator}{message}".format(separator=self.separator, uuid=uuid, date=dt_string, message=message)
        return full_message

    def __colored_message(self, message, color_set, level):
        if CndPrint.states.index(level) < self.level_index:
            return False
        if self.silent_mode is True:
            return True
        print(CndPrint.colors[color_set] + self.__build_message(message) + Bcolors.ENDC)
        return True

    def make_method(self, name, level, state):
        def _method(self, message):
            return self.__colored_message(message, level, state)
        return _method
