from mem_edit import Process
from mem_edit.utils import ctypes_equal
import ctypes

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
            ('BaseAddress', ctypes.c_ulong),
            ('AllocationBase', ctypes.c_void_p),
            ]

pid = Process.get_pid_by_name('python.exe')
if not pid:
    pid = Process.get_pid_by_name('python3')

with Process.open_process(pid) as p:
    mbi = MEMORY_BASIC_INFORMATION()
    mbi.BaseAddress = 1234567890

    addrs = p.search_all_memory(mbi)
    print(addrs)

    mbi.BaseAddress = 5555
    p.write_memory(addrs[0], mbi)

    q = p.read_memory(addrs[0], ctypes.c_ulong())
    print(q)
 
