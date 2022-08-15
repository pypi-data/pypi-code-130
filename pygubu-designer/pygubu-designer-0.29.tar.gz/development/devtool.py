import shlex
import pathlib
import subprocess as sp


PROJECT_DIR = pathlib.Path(__file__).parent.parent
SRC_DIR = PROJECT_DIR / "src"
DATA_DIR = SRC_DIR / "pygubudesigner" / "data"
PYGUBU_SRC_DIR = pathlib.Path("..") / PROJECT_DIR.parent / "pygubu" / "src"

locale_dir = DATA_DIR / "locale"


def create_pot():
    pot_path = locale_dir / "pygubu-designer.pot"
    cmd = f"""xgettext -L glade --output={pot_path} $(find ./{DATA_DIR/"ui"} -name "*.ui")"""
    print(cmd)

    cmd = f"""xgettext --join-existing -L Python --keyword=_ --output={pot_path} --from-code=UTF-8 $(find ./{SRC_DIR} -name "*.py")"""
    print(cmd)

    pot_path = DATA_DIR / "locale" / "pygubu.pot"
    cmd = f"""xgettext --join-existing -L Python --keyword=_ --output={pot_path} --from-code=UTF-8 $(find {PYGUBU_SRC_DIR} -name "*.py")"""
    print(cmd)


def update_po():
    pot_path = locale_dir / "pygubu-designer.pot"
    # update designer po files
    for f in locale_dir.glob("*/*/pygubu-designer.po"):
        cmd = f"msgmerge --verbose {f} {pot_path} -U"
        sp.run(shlex.split(cmd))

    pot_path = DATA_DIR / "locale" / "pygubu.pot"
    # update pygubu po files
    for f in locale_dir.glob("*/*/pygubu.po"):
        cmd = f"msgmerge --verbose {f} {pot_path} -U"
        sp.run(shlex.split(cmd))


def main():
    # create_pot()
    update_po()


if __name__ == "__main__":
    main()
