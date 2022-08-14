import os.path
import pathlib
import platform
import subprocess
import time

from Pxucz.utils import clear


def build(withconsole, path):
    try:
        system = platform.system()

        if system == "Windows":
            clear.run(path=os.path.dirname(path))

            buildfile_name = os.path.basename(path)
            Output_dir_name = f"{pathlib.Path(path).stem}_build"
            icon = os.path.join(os.path.dirname(path), "Icon/OUHO.ico")
            IconFolder = os.path.join(os.path.dirname(path), "Icon")
            ConfigFolder = os.path.join(os.path.dirname(path), "Config")
            FontFolder = os.path.join(os.path.dirname(path), "Font")
            ResourcesFolder = os.path.join(os.path.dirname(path), "Resources")

            if withconsole:
                command = (
                    f"python -m nuitka --mingw64 --show-modules --follow-imports "
                    f"--windows-company-name=QU4R7Z --windows-product-version={config.version} "
                    f"--output-dir={Output_dir_name} --verbose --assume-yes-for-downloads "
                    f"--windows-icon-from-ico={icon} --onefile "
                    f"--include-data-dir={IconFolder}=Icon "
                    f"--include-data-dir={ConfigFolder}=Config "
                    f"--include-data-dir={FontFolder}=Font "
                    f"--include-data-dir={ResourcesFolder}=Resources "
                    f"{buildfile_name}"
                )
            else:
                command = (
                    f"python -m nuitka --mingw64 --show-modules --follow-imports "
                    f"--windows-company-name=QU4R7Z --windows-product-version={config.version} "
                    f"--output-dir={Output_dir_name} --verbose --assume-yes-for-downloads "
                    f"--windows-icon-from-ico={icon} --onefile "
                    f"--include-data-dir={IconFolder}=Icon "
                    f"--include-data-dir={ConfigFolder}=Config "
                    f"--include-data-dir={FontFolder}=Font "
                    f"--include-data-dir={ResourcesFolder}=Resources "
                    f"--windows-disable-console "
                    f"{buildfile_name}"
                )

            start = time.time()
            subprocess.run(command.split(" "), shell=True, check=True)
            end = time.time()

            print(f"{end - start}s 사용됨")
            print(command)

        elif system == "Linux":
            print(system)
        elif system == "Darwin":
            print(system)
        else:
            print("OS를 알 수 없음")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    build(withconsole=True)
