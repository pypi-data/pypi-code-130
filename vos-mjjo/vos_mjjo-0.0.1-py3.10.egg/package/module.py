from datetime import datetime
from typing import Optional
from symspellpy import SymSpell, Verbosity


class CorDate():
    def __init__(self):
        self.sym_spell = SymSpell()
        self.dictionary_path = 'package/date_dictionary.txt'
        self.this_year = datetime.now().year
        self.this_year_two_length = int(str(self.this_year)[2:])
        self.max_edit_distance = 2
        
    def load_date_dictionary(self):
        try:
            self.sym_spell.load_dictionary(self.dictionary_path, 0, 1, separator="$")
            return True
        except:
            return False

    def get_correct_array(
        self, 
        date: str
    ) -> list:
        """Example Text

        """
        if not isinstance(date, str):
            raise TypeError("type of object must be string")
        dates = check_correct_ymd(date, self.this_year)
        if check_two_length_year(dates):
            dates = get_Four_length_year(dates)
        return dates

    def get_correct_one(
        self, 
        date: str
    ) -> str:
        """Example Text

        """
        if not isinstance(date, str):
            raise TypeError("type of object must be string")
        return get_correct_date_from_dates(check_correct_ymd(date, self.this_year), self.this_year_two_length)

    def look_up_array(
        self,
        date : str,
        max_edit_distance : Optional[int] = None,
    ) -> list:
        """Example Text

        """
        if not isinstance(date, str):
            raise TypeError("type of object('date') must be string")
        if max_edit_distance is None:
            max_edit_distance = self.max_edit_distance
        if max_edit_distance > self.max_edit_distance:
            raise ValueError("distance too large")
        suggestions = self.sym_spell.lookup(
            date,
            Verbosity.ALL,
            max_edit_distance=max_edit_distance
        )
        return suggestions

    def look_up_one(
        self,
        date : str,
        max_edit_distance : Optional[int] = None,
    ):
        """Example Text

        """
        if not isinstance(date, str):
            raise TypeError("type of object('date') must be string")
        if max_edit_distance is None:
            max_edit_distance = self.max_edit_distance
        if max_edit_distance > self.max_edit_distance:
            raise ValueError("distance too large")
    
        suggestions = self.sym_spell.lookup(
            date,
            Verbosity.ALL,
            max_edit_distance=max_edit_distance
        )
        suggestion = suggestions[0]
        return suggestion

def convert_type_year(y):
            if y == '':
                return 0
            else:
                return int(y)

def convert_type_month_day(md):
    if md in ['', '0', '00']:
        return 1
    else:
        return int(md)

def check_correct_ymd(date, this_year):
    candidate_dates = set()
    for idx_day in range(3):
        for idx_month in range(3):
            try:
                d, e_date = date[len(date)-idx_day:], date[:len(date)-idx_day]
                m, y = e_date[len(e_date)-idx_month:], e_date[:len(e_date)-idx_month]
                d = convert_type_month_day(d)
                m = convert_type_month_day(m)
                y = convert_type_year(y)
                candidate_date = datetime(y, m, d)
                if (y > 0) and (y < (this_year +1)) and candidate_date:
                    candidate_date = candidate_date.strftime("%Y%m%d")
                    candidate_dates.add(candidate_date)
            except:
                pass
    return list(candidate_dates)

def check_two_length_year(dates):
    if dates and all(1000 > int(ymd[:4]) for ymd in dates):
        return True
    else:
        return False

def change_four_length_year(year, this_year_two_length):
    if year[0] == '0':
        if year[1] == '0':
            if year[2] == '0': # 00090101처럼 000으로 시작되는 경우
                pass
            else:
                if int(year) in list(range(0, this_year_two_length)):
                    year = '20' + year[2:]
                else:
                    year = '19' + year[2:]
        else:
            year = '1' + year[1:]
    return year

def get_Four_length_year(dates, this_year_two_length):
    new_candidate_dates = list()
    for date in dates:
        date = change_four_length_year(date[:4], this_year_two_length) + date[4:]
        new_candidate_dates.append(date)
    return new_candidate_dates

def get_one_date(dates):
    # 가장 최신값
    try:
        return sorted(dates, reverse=True)[0]
    except:
        return None

def get_correct_date_from_dates(dates, this_year_two_length):
    if check_two_length_year(dates):
        dates = get_Four_length_year(dates, this_year_two_length)
    return get_one_date(dates)
