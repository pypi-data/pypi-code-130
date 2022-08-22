class Beer:
    """Beer model."""

    def __init__(self, response_json):
        self.id = response_json.get("id")
        self.name = response_json.get("name")
        self.tagline = response_json.get("tagline")
        self.first_brewed = response_json.get("first_brewed")
        self.description = response_json.get("description")
        self.image_url = response_json.get("image_url")
        self.abv = response_json.get("abv")
        self.ibu = response_json.get("ibu")
        self.target_fg = response_json.get("target_fg")
        self.target_og = response_json.get("target_og")
        self.ebc = response_json.get("ebc")
        self.srm = response_json.get("srm")
        self.ph = response_json.get("ph")
        self.attenuation_level = response_json.get("attenuation_level")
        self.volume = Measurement(response_json.get("volume"))
        self.boil_volume = Measurement(response_json.get("boil_volume"))
        self.method = Method(response_json.get("method"))
        self.ingredients = AllIngredients(response_json.get("ingredients"))
        self.food_pairing = response_json.get("food_pairing")
        self.brewers_tips = response_json.get("brewers_tips")
        self.contributed_by = response_json.get("contributed_by")

    def __str__(self):
        return f"{self.id}, {self.name}, {self.tagline}, {self.first_brewed}"

    def __eq__(self, beer) -> bool:
        for attribute in self.__dict__.keys():
            if not self.__dict__[attribute] == beer.__dict__[attribute]:
                return False
        return True


class Measurement:
    """Measurement model."""

    def __init__(self, volume):
        self.value = volume.get("value")
        self.unit = volume.get("unit")

    def __str__(self):
        return f"{self.value} {self.unit}"

    def __eq__(self, measurement) -> bool:
        for attribute in self.__dict__.keys():
            if not self.__dict__[attribute] == measurement.__dict__[attribute]:
                return False
        return True


class TemperatureAndDuration:
    """Temperature and duration model."""

    def __init__(self, temp, duration=None):
        self.temp = Measurement(temp)
        self.duration = duration

    def __str__(self):
        return (
            f"{self.temp} for {self.duration} mins" if self.duration else f"{self.temp}"
        )

    def __eq__(self, temperatureDuration) -> bool:
        for attribute in self.__dict__.keys():
            if not self.__dict__[attribute] == temperatureDuration.__dict__[attribute]:
                return False
        return True


class Method:
    """Method model."""

    def __init__(self, method):
        self.mash_temp = [
            TemperatureAndDuration(
                temp=measurement.get("temp"), duration=measurement.get("duration")
            )
            for measurement in method.get("mash_temp")
        ]
        self.fermentation = TemperatureAndDuration(
            temp=method.get("fermentation").get("temp")
        )
        self.twist = method.get("twist")

    def __str__(self):
        string = "Mash Temp: " + ", ".join(map(str, self.mash_temp))
        string += f"\nFermentation: {self.fermentation}"
        if self.twist:
            string += f"\nTwist: {self.twist}"
        return string

    def __eq__(self, method) -> bool:
        for attribute in self.__dict__.keys():
            if not self.__dict__[attribute] == method.__dict__[attribute]:
                return False
        return True


class AllIngredients:
    """All ingredients model."""

    def __init__(self, ingredients):
        self.malt = [
            Ingredient(ingredient.get("name"), ingredient.get("amount"))
            for ingredient in ingredients.get("malt")
        ]
        self.hops = [
            Ingredient(
                ingredient.get("name"),
                ingredient.get("amount"),
                ingredient.get("add"),
                ingredient.get("attribute"),
            )
            for ingredient in ingredients.get("hops")
        ]
        self.yeast = ingredients.get("yeast")

    def __str__(self):
        return (
            f"Malt -> {''.join(map(str, self.malt))}\n"
            f"Hops -> {', '.join(map(str, self.hops))}\n"
            f"Yeast: {self.yeast}"
        )

    def __eq__(self, allIngredients) -> bool:
        for attribute in self.__dict__.keys():
            if not self.__dict__[attribute] == allIngredients.__dict__[attribute]:
                return False
        return True


class Ingredient:
    """Ingredient model."""

    def __init__(self, name, amount, add=None, attribute=None):
        self.name = name
        self.amount = Measurement(amount)
        self.add = add
        self.attribute = attribute

    def __str__(self):
        string = f"\n\t{self.name}: {self.amount}"
        if self.add:
            string += f", {self.add}"
        if self.attribute:
            string += f", {self.attribute}"

        return string

    def __eq__(self, ingredient) -> bool:
        for attribute in self.__dict__.keys():
            if not self.__dict__[attribute] == ingredient.__dict__[attribute]:
                return False
        return True
