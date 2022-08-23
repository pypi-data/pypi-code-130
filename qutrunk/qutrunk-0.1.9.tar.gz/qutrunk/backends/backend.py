from abc import ABCMeta, abstractmethod


class Backend(metaclass=ABCMeta):
    """
    Basic simulator: All simulators are derived from this class.
    """
    @abstractmethod
    def send_circuit(self, circuit, final=False):
        """
        send the quantum circuit to backend
        """
        pass
