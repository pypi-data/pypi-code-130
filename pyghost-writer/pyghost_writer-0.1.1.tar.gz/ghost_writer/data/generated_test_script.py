from ghost_writer import ScriptGenerator


class NewGenerator(ScriptGenerator):
    def __init__(self, file_name: str) -> None:
        super().__init__(file_name)

    def _build_script(self) -> None:
        self._add_line('import os')
        self._end_line()
        self._end_line()
        self._add_line('for i in range(10):')
        self._add_line('for j in range(20):', indent_level=1)
        self._add_line('pass', indent_level=2)
