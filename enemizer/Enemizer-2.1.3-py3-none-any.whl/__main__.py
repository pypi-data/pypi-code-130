import botw_flag_util.generator as flag_util
import json
import shutil

from bcml.install import install_mod, link_master_mod
from bcml.util import get_settings, get_game_file
from enemizer.enemizer import Enemizer
from enemizer.enemizer_config import EnemizerConfig
from enemizer.generator import Generator
from pathlib import Path


WELCOME = str(
    "    /\\                          /\\\n"
    + "   /__\\     Welcome to the     /__\\\n"
    + "  /\\  /\\   BotW Ene-mizer!    /\\  /\\\n"
    + " /__\\/__\\                    /__\\/__\\\n"
    + "\n"
    + "Customize settings (y/N) "
)


def main():

    opt: EnemizerConfig = EnemizerConfig()

    # Assign options
    if input(WELCOME) == "y":

        print(
            "Enter 'y' or 'n' for the following options:\n\n"
            + "\tRandomize enemies in..."
        )

        # Assign randomized locations
        opt.main_field = input("\t\tOverworld (Y/n) ").lower() != "n"
        opt.shrines = input("\t\tShrines (Y/n) ").lower() != "n"
        opt.divine_beasts = input("\t\tDivine Beasts (Y/n) ").lower() != "n"
        opt.aoc_field = input("\t\tThe Trial of the Sword (Y/n) ").lower() != "n"

        # Assign misc options
        opt.chaos = (
            input(
                "\n\tChaos Mode: All enemies have an equal chance of spawning (NOT RECOMMENDED)\n"
                + "\t\tActivate Chaos mode? (y/N) "
            ).lower()
            == "y"
        )

        if not opt.chaos:

            _boss_prob = input(
                "\n\tChoose the spawn probability of mini-bosses.\n"
                + "\t\tEnter a number from 1-100 (leave empty for the default value): "
            )

            while (_boss_prob != ""):
                try:
                    opt.boss_prob = int(_boss_prob)
                    break
                except:
                    _boss_prob = input(
                        f"{_boss_prob} is not a valid number. Please enter a number: "
                    )

    # Randomize enemies
    print("Randomizing. . .")
    Enemizer(opt).randomize()

    # Generate flags
    print("Generating flags. . .")
    bootup_path = Path("Enemized\\content\\Pack\\Bootup.pack")
    bootup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(get_game_file("Pack/Bootup.pack"), bootup_path)
    flag_util.generate(Generator(get_settings("wiiu")))

    # Install mod
    if (input("Install mod? (Y/n) ").lower() == "y"):
        print("Installing. . .")
        mod_path = Path("Enemized\\info.json")
        mod_meta = {
            "name": "Enemizer v2 by Echocolat",
            "image": "",
            "url": "",
            "desc": "",
            "version": "2.0.0",
            "options": {},
            "depends": [],
            "showCompare": False,
            "showConvert": False,
            "platform": "wiiu" if get_settings("wiiu") == True else "switch",
            "id": "",
        }

    mod_path.write_text(json.dumps(mod_meta))
    install_mod(mod=mod_path, merge_now=True)
    link_master_mod()
    


if __name__ == "__main__":
    main()
