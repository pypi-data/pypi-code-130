import logging
import re
import sys
import time

import restructuredtext_lint
from git import Repo

formatter = logging.Formatter("%(name)s :: %(levelname)s :: %(message)s")
steam_handler = logging.StreamHandler()
# steam_handler = logging.FileHandler('logging.conf')
steam_handler.setLevel(logging.DEBUG)
steam_handler.setFormatter(formatter)

# création de l'objet logger qui va nous servir à écrire dans les logs
logger = logging.getLogger("precommit")
# on met le niveau du logger à DEBUG, comme ça il écrit tout
logger.setLevel(logging.WARNING)
logger.addHandler(steam_handler)

# Files selection


def get_commited_files(repo):
    hdiff = repo.head.commit.diff()
    diff = {"A": [], "M": []}
    for f in hdiff.iter_change_type("A"):
        diff["A"].append(f.b_path)
    for f in hdiff.iter_change_type("M"):
        diff["M"].append(f.b_path)

    return diff


def select_by_extension(files, ext="rst"):
    return [i for i in files if i.split(".")[-1] == ext and "skeleton" not in i]


# Rst linter


def rst_lint(filename):
    with open(filename, "r") as f:
        errors = restructuredtext_lint.lint(f.read())
    for e in errors:
        logger.warning(f"{filename} \n{e.full_message}\n")
    return errors


# Rst parameters normalize


def normalize_file(filename, normalizers={}):
    logger.debug(f"Normalizing {filename}")
    logger.debug(f"With {normalizers}")
    new_file = ""
    modified_lines = []
    with open(filename, "r") as f:
        for l in f.readlines():
            new_line = run_normalizers(l, normalizers)
            if new_line != l:
                modified_lines.append(f"{l}")
                logger.warning(f"{filename}\n\t{l}\t{new_line}")
            new_file += new_line

    with open(filename, "w") as f:
        f.write(new_file)
    logger.debug(f"{filename} written")

    return modified_lines


def run_normalizers(line, normalizers):
    for c in normalizers:
        obs = re.search(c, line)
        if obs:
            logger.debug(f"Find for {c}")
            return normalizers[c](line)
    return line


# Rst function tools


def update_date(line):
    date = time.strftime("%Y-%m-%d")
    logger.debug(f"Update Date to: {date}")
    return f":date: {date}\n"


def update_modified(line):
    modified = time.strftime("%Y-%m-%d")
    logger.debug(f"Update modified to: {modified}")
    return f":modified: {modified}\n"


def normalize_tags(line):
    logger.debug(f"Normaizing tags")
    tags = line.split(":")[-1]
    tags = [i.strip().capitalize() for i in tags.split(",")]
    tags_str = ", ".join(tags)
    logger.debug(f"Update tags to: {tags_str}")
    return f":tags: {tags_str}\n"


NORMALIZERS_MODIFIED = {
    ":modified:.*": update_modified,
    ":tags:.*": normalize_tags,
}

NORMALIZERS_NEW = {
    ":date:.*": update_date,
    ":modified:.*": update_modified,
    ":tags:.*": normalize_tags,
}


def main(argv: list[str] = None) -> int:
    r = Repo()
    diff = get_commited_files(r)

    errors = []
    modified = []

    # New files
    for f in select_by_extension(diff["A"], "rst"):
        errors += rst_lint(f)
        modified += normalize_file(f, NORMALIZERS_NEW)
        r.index.add([f])
    # Modified files
    for f in select_by_extension(diff["M"], "rst"):
        errors += rst_lint(f)
        modified += normalize_file(f, NORMALIZERS_MODIFIED)
        r.index.add([f])

    return int(len(errors) > 0)


if __name__ == "__main__":
    main()
