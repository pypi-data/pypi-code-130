from .api_object import ApiObject


class Character(ApiObject):

    @classmethod
    def get_endpoint(cls, _id):
        if _id:
            return f"/character/{_id}"
        return "/character"

    def __init__(self, _id: str = "",
                 name: str = "",
                 height: str = "",
                 race: str = "",
                 gender: str = "",
                 birth: str = "",
                 spouse: str = "",
                 death: str = "",
                 realm: str = "",
                 hair: str = "",
                 wikiUrl: str = ""):
        self._id = _id
        self.name = name
        self.height = height
        self.race = race
        self.gender = gender
        self.birth = birth
        self.spouse = spouse
        self.death = death
        self.realm = realm
        self.hair = hair
        self.wiki_url = wikiUrl

