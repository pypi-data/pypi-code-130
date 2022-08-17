from .api_object import ApiObject


class Movie(ApiObject):

    @classmethod
    def get_endpoint(cls, _id):
        if _id:
            return f"/movie/{_id}"
        return "/movie"

    def __init__(self, _id: str = "",
                 name: str = "",
                 runtimeInMinutes: int = "",
                 budgetInMillions: int = "",
                 boxOfficeRevenueInMillions: int = "",
                 academyAwardNominations: int = "",
                 academyAwardWins: int = "",
                 rottenTomatoesScore: int = ""):
        self._id = _id
        self.name = name
        self.runtime_in_minutes = runtimeInMinutes
        self.budget_in_millions = budgetInMillions
        self.box_office_revenue_in_millions = boxOfficeRevenueInMillions
        self.academy_award_nominations = academyAwardNominations
        self.academy_award_wins = academyAwardWins
        self.rotten_tomatoes_score = rottenTomatoesScore

