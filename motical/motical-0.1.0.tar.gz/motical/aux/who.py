"""Retrieve information from World Health Organization website."""

DEFAULT_LIFE_EXP_BY_COUNTRY_URL = (
    "https://apps.who.int/"
    "gho/athena/api/GHO/WHOSIS_000001?"
    "format=json&profile=simple&filter=COUNTRY:{country}"
)


def get_life_expectancy_at_birth(country: str):
    """Get Life expectancy data by country.

    :param country: str: country code
    """
    print(country)
