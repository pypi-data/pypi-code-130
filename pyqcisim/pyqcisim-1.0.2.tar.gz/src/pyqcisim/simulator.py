from pyqcisim.QCIS_parser import QCISParser
from pyqcisim.circuit_executor import CircuitExecutor
from pyqcisim.utils import count_final_result


class PyQCISim(object):
    """
    A Python-based Quantum Control Instrument Set (QCIS) program simulator.

    Attributes:
        _program: The QCIS program to be simulated
        _parser: A QCIS parser
        _circuit_executor: A quantum circuit simulator executing QCISInst
        _compile_success: The error code for compilation
        _instructions: Generated QCIS instructions by parser
        _executed: The flag for whether instructions have been executed (not used yet)
    """

    def __init__(self):
        self._program = ""
        self._parser = None
        self._circuit_executor = None

        self._compile_success = False
        self._instructions = []
        self._executed = False

    def compile(self, prog):
        self._program = prog
        self._parser = QCISParser()  # Parser is also refreshed for a new compile

        success, instructions, names = self._parser.parse(self._program)
        if not success:
            print(self._parser.error_list)
            raise ValueError(
                "QCIS parser failed to compile the given QCIS program.")
        self._compile_success = success
        self._instructions = instructions
        self._circuit_executor = CircuitExecutor(names)

    def simulate(self, mode="one_shot", num_shots=1000):
        '''Simulate the compiled QCIS program.

        Args:
          - mode (string): the simulation mode to use:
              - "one_shot": the simulation result is a dictionary with each key being a qubit
                  measured, and the value is the outcome of measuring this qubit.
              - "final_state": the simulation result is a two-level dictionary:
                  {
                    'classical': {'Q1': 1, 'Q2': 0},
                    'quantum': (['Q3', 'Q4'], array([0, 1, 0, 0]))
                  }
          - num_shots (int): the number of iterations performed in `one_shot` mode.
        '''
        if not self._compile_success:
            raise ValueError("Failed to simulate due to compilation error.")

        if mode == "one_shot":
            one_shot_msmts = []
            for i in range(num_shots):
                self._circuit_executor.reset()  # Reset the quantum state simulator

                for inst in self._instructions:  # Execute instructions one by one.
                    # print("execute {}...".format(inst))
                    self._circuit_executor.execute(inst)

                # Pending operations will not be done!
                # As they do not contribute to the measurement results!
                one_shot_msmts.append(self._circuit_executor.res)

            final_result = count_final_result(one_shot_msmts)

        elif mode == "final_state":
            self._circuit_executor.reset()  # Reset the quantum state simulator
            for inst in self._instructions:  # Execute instructions one by one.
                # print("execute {}...".format(inst))
                self._circuit_executor.execute(inst)
            final_result = self._circuit_executor.get_quantum_state()

        else:
            raise ValueError(
                "Invalid simulation mode: '{}' (supported are: 'one_shot' and "
                "'final_state').".format(mode)
            )

        return final_result
