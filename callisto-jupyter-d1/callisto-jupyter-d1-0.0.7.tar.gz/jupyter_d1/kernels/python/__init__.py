from pathlib import Path
from typing import List

from ..kernel_definition import KernelDefinition
from .vars_manager import PythonVarsManager, VarsManager
from .workdir_manager import PythonWorkDirManager, WorkDirManager


class PythonKernelDefinition(KernelDefinition):
    def create_vars_manager(self) -> VarsManager:
        return PythonVarsManager()

    def create_workdir_manager(self, workdir: str) -> WorkDirManager:
        return PythonWorkDirManager(workdir)

    @property
    def kernel_options(self) -> List[str]:
        return [
            f"--IPKernelApp.exec_files=['{Path(__file__).parent.resolve()}"
            f"/startup/callisto_startup.py']"
        ]


kernel_definition = PythonKernelDefinition()
