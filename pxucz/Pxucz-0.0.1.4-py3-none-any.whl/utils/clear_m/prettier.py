import os
import subprocess
import platform


def run(path):
    try:
        system = platform.system()
        l_py_files = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".py") and root.find("venv") == -1:
                    l_py_files.append(os.path.join(root, file))

        print("prettier", l_py_files)
        if system == "Windows":
            for i in l_py_files:
                command = f"black {i}"
                subprocess.run(command, shell=True)

        elif system == "Linux":
            print(system)
        elif system == "Darwin":
            print(system)
        else:
            print("OS를 알 수 없음")
    except Exception as e:
        print(e)
