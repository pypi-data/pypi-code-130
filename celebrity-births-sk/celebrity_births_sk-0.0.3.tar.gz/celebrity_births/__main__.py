"""
_summary_
"""
from celebrity_births.date import Date
from celebrity_births.scraper import Scraper

print("Welcome to this mock package")
print(
    "Introduce a date and I will print a list of celebrities"
    + " that were born that day"
)

day = int(input("Introduce the day: "))
month = int(input("Introduce the month: "))

date_object = Date(day, month)
date = date_object.to_wiki_format()

scraper = Scraper()

celebrities = scraper.get_celebrities(date)

for i in celebrities:
    print(i)
