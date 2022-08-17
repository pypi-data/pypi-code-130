from bcml.util import get_aoc_dir, get_game_dir


class EnemizerConfig:

    # Location options
    aoc_field: bool = True
    main_field: bool = True
    remains: bool = True
    shrines: bool = True

    #:bool Misc options
    chaos: bool = False
    boss_prob: int = 23
    random_weapons: bool = True
    sandworm_allowed: bool = True

    def get_map_paths(self) -> dict:

        # return if not applicable
        if self.main_field == False and self.aoc_field == False:
            return {}

        letters: str = "ABCDEFGHIJ"
        numbers: int = 8
        types: list = ["Dynamic", "Static"]

        fields: list = []
        if self.aoc_field == True:
            fields.append("Aoc")
        if self.main_field == True:
            fields.append("Main")

        def normalize(field, letter, number, map_type) -> str:
            return f"{field}Field\\{letter}-{number+1}\\{letter}-{number+1}_{map_type}.smubin"

        return {
            f"{get_aoc_dir()}\\Map\\{normalize(field, letter, number, map_type)}": f"Enemized\\aoc\\0010\\Map\\{normalize(field, letter, number, map_type)}"
            for letter in letters
            for number in range(numbers)
            for field in fields
            for map_type in types
        }

    def get_dungeon_packs(self) -> dict:

        # return if not applicable
        if self.shrines == False:
            return {}

        game_count: int = 119
        dlc_count = range(120, 137)

        def normalize(i: int) -> str:
            return (
                "00" if len(str(i)) == 1 else "0" if len(str(i)) == 2 else ""
            ) + str(i)

        file_map = {
            f"{get_game_dir()}\\Pack\\Dungeon{normalize(i)}.pack": f"Enemized\\content\\Pack\\Dungeon{normalize(i)}.pack"
            for i in range(game_count + 1)
        }

        for i in dlc_count:
            file_map[
                f"{get_aoc_dir()}\\Pack\\Dungeon{normalize(i)}.pack"
            ] = f"Enemized\\aoc\\0010\\Pack\\Dungeon{normalize(i)}.pack"

        return file_map

    def get_remains_packs(self) -> dict:

        # return if not applicable
        if self.remains == False:
            return {}

        return {
            f"{get_game_dir()}\\Pack\\Remains{element}.pack": f"Enemized\\aoc\\0010\\Pack\\Remains{element}.pack"
            for element in ["Electric", "Fire", "Water", "Wind"]
        }
