from .quote import Quote


class CharacterQuote(Quote):

    @classmethod
    def get_endpoint(cls, character_id):
        if not character_id:
            raise RuntimeError("CharacterQuote requires character_id")
        return f"/character/{character_id}/quote"

