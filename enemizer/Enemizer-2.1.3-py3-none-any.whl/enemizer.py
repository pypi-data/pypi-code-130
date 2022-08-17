import oead

from enemizer.enemizer_config import EnemizerConfig
from pathlib import Path
from random import randint, choice
from enemizer.utils import DEFAULTS, get_evaluated_weights, get_item_table, is_enemy, to_oead, get_item_tables


class Enemizer:
    def __init__(self, ops: EnemizerConfig):
        self.arrow_weights = get_evaluated_weights("Arrows")
        self.boss_weights = get_evaluated_weights("Bosses")
        self.config = ops
        self.weights = get_evaluated_weights("Enemies")

    arrow_weights: list
    boss_weights: list
    config: EnemizerConfig = EnemizerConfig()
    weights: list
    generated: dict = {
        "Bokoblin": 0,
        "Moriblin": 0,
        "Lizalfos": 0,
        "Lynel": 0,
        "Keese": 0,
        "Chuchu": 0,
        "Golem_Little": 0,
        "Guardian_Mini": 0,
        "Guardian": 0,
        "Octarock": 0,
        "Wizzrobe": 0,
        "Giant": 0,
        "Golem": 0,
        "Sandworm": 0,
    }

    def randomize(self):

        functions = {
            self.config.get_map_paths: self.get_randomized_map,
            self.config.get_dungeon_packs: self.get_randomized_pack,
            self.config.get_remains_packs: self.get_randomized_pack,
        }

        for func1, func2 in functions.items():
            for src, dst in func1().items():
                dst_path = Path(dst)
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                dst_path.write_bytes(
                    func2(Path(src).read_bytes(), dst_path.stem.split("_")[0])
                )

        print("\n\nSuccessfully generated:")
        for key, value in self.generated.items():
            print(f"{key}: {value}")

    def get_randomized_map(self, data: bytes, map_unit: str = None) -> bytes:

        # Deserialize map file
        data = oead.byml.from_binary(oead.yaz0.decompress(data))

        # Iterate unit configs
        for unit_config in data["Objs"]:

            # Skip any non-enemy actors
            if not is_enemy(unit_config["UnitConfigName"]):
                continue

            # Set the unit config data
            enemy = self.get_random_enemy(map_unit)
            unit_config = self.set_enemy(enemy, unit_config)

            # Update the generation tracker
            for category_name in self.generated:
                if category_name in enemy:
                    self.generated[category_name] += 1
                    break

            # Set IsIchigekiActor value
            debug = dict(unit_config)
            if unit_config["HashId"] in DEFAULTS["OneHitTags"]:
                unit_config["!Parameters"]["IsIchigekiActor"] = True

            # Set random weapons
            if self.config.random_weapons == True:
                self.set_weapons(unit_config)

        if map_unit is not None:
            print(f"Randomized '{map_unit}'", end="\r")
        return oead.yaz0.compress(oead.byml.to_binary(to_oead(data), True))

    def get_randomized_pack(self, data: bytes, _) -> bytes:

        # Deserialize sarc file
        sarc = oead.Sarc(data)
        sarc_writer = oead.SarcWriter(endian=oead.Endianness.Big)

        # Iterate nested sarc files
        for file in sarc.get_files():
            if file.name.endswith(".smubin") and not file.name.endswith(
                "_NoGrudgeMerge.smubin"
            ):
                sarc_writer.files[file.name] = self.get_randomized_map(file.data)
            else:
                sarc_writer.files[file.name] = oead.Bytes(file.data)

        # Log changes
        print(f"Randomized '{_}'", end="\r")

        # Serialize sarc file
        _, sarc_bytes = sarc_writer.write()
        return sarc_bytes

    def get_random_enemy(self, map_unit: str = "") -> str:

        # Get a boss or enemy from
        # the probability lists.
        enemy: str = (
            choice(self.boss_weights + self.weights)
            if self.config.chaos == True
            else choice(self.boss_weights)
            if randint(0, self.config.boss_prob) == 0
            else choice(self.weights)
        )

        # Lower the chance of a
        # boss in blacklisted areas.
        if map_unit in DEFAULTS["BlacklistZones"] and enemy in DEFAULTS["Bosses"]:
            enemy = (
                choice(self.boss_weights)
                if randint(0, 10) == 0
                else choice(self.weights)
            )

        # Reroll sandworm actors if
        # they are are not allowed
        if "Sandworm" in enemy and not self.config.sandworm_allowed:
            while "Sandworm" in enemy:
                enemy = choice(self.weights)

        return enemy

    def set_enemy(self, enemy: str, unit_config: dict) -> dict:

        # Fix the translate values
        # for Guardian_A_Fixed actors
        if "Guardian_A_Fixed" in unit_config["UnitConfigName"]:
            if "Guardian_A_Fixed" not in enemy:
                unit_config["Translate"][1] = oead.F32(
                    float(unit_config["Translate"][1]) + 2.5
                )

        # Randomize the Talus ore
        # and sleep positions
        if "Golem" in enemy and "Little" not in enemy and enemy != "Enemy_Golem_Fire_R":

            # Force set parameters
            unit_config["!Parameters"] = (
                unit_config["!Parameters"] if "!Parameters" in unit_config else {}
            )

            # Set sleep pos mode
            unit_config["!Parameters"]["GolemSleepType"] = choice(
                ["SleepForward_B", "SleepForward_A"]
            )

            # Set ore pos mode
            unit_config["!Parameters"]["GolemWeakPointLocation"] = choice(
                ["Point_A", "Point_B", "Point_C"]
            )

        if "Giant" in enemy:

            # Force set parameters
            unit_config["!Parameters"] = (
                unit_config["!Parameters"] if "!Parameters" in unit_config else {}
            )

            # Set param types
            armors = {"GiantArmor1": "L", "GiantArmor2": "R"}

            # Purge old parameters
            for param in armors:
                if param in unit_config["!Parameters"]:
                    dict(unit_config["!Parameters"]).pop(param)

                # Randomize giant armor
                if randint(0, 2) != 0:
                    unit_config["!Parameters"][
                        param
                    ] = f"GiantGreave_{choice(['Wood', 'Iron'])}_{armors[param]}"

        # Set the UnitConfigName
        unit_config["UnitConfigName"] = enemy

        # Remove breaking values
        if "LinksToRail" in unit_config:
            dict(unit_config).pop("LinksToRail")
        if "OnlyOne" in unit_config:
            dict(unit_config).pop("OnlyOne")
        if "Scale" in unit_config:
            dict(unit_config).pop("Scale")
        if "Guardian_C" in enemy:
            unit_config["Translate"][1] = oead.F32(
                float(unit_config["Translate"][1]) + 30.0
            )
        if "Keese" in enemy:
            unit_config["Translate"][1] = oead.F32(
                float(unit_config["Translate"][1]) + 2.5
            )

        debug = dict(unit_config)
        return unit_config

    def set_weapons(self, unit_config: dict) -> dict:

        # SKIP NON WEAPON ACTORS

        # Skip actors without parameters
        if "!Parameters" not in unit_config:

            # 1/3 chance of not adding weapons
            # in cases where no parameters exist
            if randint(0, 3) != 0:
                unit_config["!Parameters"] = {}
            else:
                return unit_config

        cfn = unit_config["UnitConfigName"]
        hand_weapons = [
            "Weapon_Lsword_",
            "Weapon_Shield_",
            "Weapon_Spear_",
            "Weapon_Sword_",
        ]
        all_weapons = ["Weapon_Bow_"] + hand_weapons

        # Set mini guardian actors
        if "Enemy_Guardian_Mini" in cfn:
            unit_config = self.set_weapons_any(
                unit_config,
                hand_weapons,
                3
                if cfn.endswith("_Senior")
                else 2
                if cfn.endswith("_Middle")
                else 1
                if cfn.endswith("_Junior")
                else 0,
            )

        # Set Hinox weapons
        elif "Giant" in cfn:
            unit_config = self.set_weapons_any(unit_config, all_weapons, range(3, 5))

        # Set long sword only actors
        elif cfn in DEFAULTS["ItemTables"]["IsLswordOnly"]:
            unit_config = self.set_weapons_mapped(unit_config, {1: "Weapon_Lsword_"})

        # Set bow only actors
        elif (
            cfn in DEFAULTS["ItemTables"]["IsBowOnly"] and "!Parameters" in unit_config
        ):
            unit_config["!Parameters"]["ArrowName"] = choice(self.arrow_weights)
            unit_config = self.set_weapons_mapped(unit_config, {1: "Weapon_Bow_"})

        # Set other actors
        elif cfn not in DEFAULTS["Bosses"]:

            # Always set the arrow for all enemies
            unit_config["!Parameters"]["ArrowName"] = choice(self.arrow_weights)

            # Create 1/3 chance var
            arsenal = randint(0, 2)

            # Always set the bow for Lynels
            if "Enemy_Lynel" in cfn:
                unit_config = self.set_weapons_mapped(unit_config, {3: "Weapon_Bow_"})
                arsenal = randint(0, 1) if arsenal == 2 else arsenal

            # Choose randonly between a shield and sword and a sword/lsword/spear.
            if arsenal == 0:
                unit_config = self.set_weapons_mapped(
                    unit_config,
                    {
                        1: ["Weapon_Sword_"],
                        4 if "Enemy_Lynel" in cfn else 2: ["Weapon_Shield_"],
                    },
                )
            elif arsenal == 1:
                unit_config = self.set_weapons_mapped(
                    unit_config,
                    {1: ["Weapon_Sword_", "Weapon_Lsword_", "Weapon_Spear_"]},
                )
            else:
                unit_config = self.set_weapons_mapped(unit_config, {1: "Weapon_Bow_"})

        return unit_config

    def set_weapons_any(self, unit_config: dict, prefixes: list, set_num):
        weapons: list = get_item_tables(prefixes)
        equip_items = [
            f"EquipItem{i+1}"
            for i in (range(set_num) if type(set_num) is int else set_num)
        ]

        for equip_item in equip_items:
            unit_config["!Parameters"][equip_item] = weapons.pop(
                randint(0, len(weapons) - 1)
            )

        return unit_config

    def set_weapons_mapped(self, unit_config: dict, map: dict) -> dict:
        for key, value in map.items():
            unit_config["!Parameters"][
                key if type(key) is str else f"EquipItem{key}"
            ] = choice(get_item_tables(value))

        return unit_config
