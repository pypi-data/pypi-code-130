import argparse, os, re
from audioop import add
from datetime import date, datetime
from tkinter import filedialog
from typing import Dict, List, Tuple, Type
from sdif_toolkit.records import STROKES, RECORD_TYPES, MeetRecord, RelayNameRecord, TeamIDRecord, IndividualEventRecord, SplitsRecord, IndividualInformationRecord, RelayEventRecord
from sdif_toolkit.time import Time
from pyodbc import connect

RESULT_TYPES = {
    "p": "Prelims",
    "s": "Swim-Off",
    "f": "Finals"
}

GENDERS_BG = {
    "m": "Boys",
    "f": "Girls"
}

class Result:
    time: Time
    course: str
    type: str
    splits: Dict[int, Time]
    split_distance: int
    rank: int
    points: float

    def __init__(self, time:Time=None, time_str:str=None, type=None, course=None, splits=[], split_distance=None, rank=None, points=None) -> None:
        if time is not None:
            self.time = time
        elif time_str is not None:
            self.time = Time(time_str)
        
        if type is not None:
            self.type = type

        if course is not None:
            self.course = course

        if rank is not None:
            self.rank = int(rank)
        
        if points is not None:
            self.points = float(points)
        
        self.splits = {}
        

    def __repr__(self) -> str:
        return f"{self.time}"

class Seed:
    time: Time
    course: str
    heat: int
    lane: int
    rank: int

    def __init__(self, time:Time=None, time_str:str=None, course=None, heat=None, lane=None, rank=None) -> None:
        if time is not None:
            self.time = time
        elif time_str is not None:
            self.time = Time(time_str)

        if course is not None:
            self.course = course

        if heat is not None:
            self.heat = int(heat)

        if lane is not None:
            self.lane = int(lane)

        if rank is not None:
            self.rank = int(rank)

    def __repr__(self) -> str:
        return f"{self.time}"

class AgeGroup:
    lower_age: int
    upper_age: int

    def __init__(self, lower_age:int, upper_age:int) -> None:
        self.lower_age = lower_age
        self.upper_age = upper_age

    def __repr__(self) -> str:
        if self.lower_age > 0 and self.upper_age < 100:
            return f"{self.lower_age}-{self.upper_age}"
        elif self.lower_age <= 0 and self.upper_age < 100:
            return f"{self.upper_age} & Under"
        elif self.lower_age > 0 and self.upper_age >= 100:
            return f"{self.lower_age} & Over"
        else:
            return "Open"

class Event:
    number: str
    distance: int
    stroke: str
    age_group: AgeGroup
    gender: str

    def __init__(self, number:str, distance:int|str|float, stroke:str, age_group:AgeGroup, gender:str) -> None:
        self.number = number
        if type(distance) is str or type(distance) is float:
            self.distance = int(distance)
        elif type(distance) is int:
            self.distance = distance
        self.stroke= stroke
        self.age_group = age_group
        self.gender = gender.lower()

    def __repr__(self) -> str:
        return f"{GENDERS_BG[self.gender]} {self.age_group} {self.distance} {self.stroke}"


class Swimmer:
    first_name: str
    pref_name: str
    middle_name: str
    last_name: str
    birthdate: str
    age: int

    def __init__(self, full_name, age=None, birthdate=None, pref_name=None) -> None:
        name = parse_name(full_name)
        self.first_name = name["first_name"]
        if "middle_name" in name.keys():
            self.middle_name = name["middle_name"]
        else:
            self.middle_name = ""
        self.last_name = name["last_name"]

        if type(age) is str:
            self.age = int(age)
        elif type(age) is int:
            self.age = age
        
        if birthdate is not None:
            self.birthdate = birthdate

        if pref_name is not None:
            self.pref_name = pref_name

    @property
    def id(self):
        birthdate = self.birthdate
        first = self.first_name[0:3].ljust(3,"*").upper()
        middle = self.middle_name[0:1].ljust(1,"*").upper()
        last = self.last_name[0:4].ljust(4,"*").upper()
        return f"{birthdate}{first}{middle}{last}" 

    def __repr__(self) -> str:
        return self.full_pref_name

    @property
    def full_name(self):
        if hasattr(self, "middle_name"):
            return f"{self.last_name}, {self.first_name} {self.middle_name}"
        else:
            return f"{self.last_name}, {self.first_name}"

    @property
    def full_pref_name(self):
        first = self.pref_name if hasattr(self, "pref_name") else self.first_name
        return f"{self.last_name}, {first}"

class IndividualEntry:
    event: Event
    swimmer: Swimmer
    seeds: Dict[str, Seed]
    results: Dict[str, Result]

    def __init__(self) -> None:
        self.seeds = {}
        self.results = {}

    def __repr__(self) -> str:
        return f"{self.swimmer} - {self.event}"

class RelayEntry:
    event: Event
    identifier: str
    swimmers: Dict[str, Dict[int,Swimmer]]
    seeds: Dict[str, Seed]
    results: Dict[str, Result]

    def __init__(self) -> None:
        self.swimmers = {}
        self.seeds = {}
        self.results = {}

    def __repr__(self) -> str:
        return f"{self.event} - {self.identifier}"

class Team:
    name: str
    code: str
    lsc: str
    swimmers: Dict[str, Swimmer]

    @property
    def points(self) -> float:
        individual_points = [entry.results["f"].points for entry in self.entries if "f" in entry.results and hasattr(entry.results["f"], "points")]
        ind_total = sum(individual_points)
        relay_points = [relay.results["f"].points for relay in self.relays if "f" in relay.results and hasattr(relay.results["f"], "points")]
        relay_total = sum(relay_points)
        total = ind_total + relay_total
        return total


    def __init__(self, name, code, lsc) -> None:
        self.name = name
        self.code = code
        self.lsc = lsc
        self.swimmers = {}
        self.entries = []
        self.relays = []

    def __repr__(self) -> str:
        return f"{self.name}"

class Session:
    name: str
    start: datetime
    events: List[Event]
    course: str

    def __init__(self, name, start, course) -> None:
        self.name = name
        self.start = start
        self.course = course
        self.events = {}

    def __repr__(self) -> str:
        return self.name

class Facility:
    name: str
    address1: str
    address2: str
    city: str
    state: str
    zip: str

    def __init__(self, name, address1, address2, city, state, zip) -> None:
        self.name = name
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.zip = zip

    def __repr__(self) -> str:
        return f"{self.name}"

class Meet:
    name: str
    facility: Facility
    start_date: date
    end_date: date
    sessions: List[Session]
    events: Dict[str, Event]
    teams: Dict[str, Team]
    entries: Dict[Tuple[str,str], IndividualEntry]
    relays: Dict[Tuple[str,str,str], RelayEntry]

    def __init__(self) -> None:
        self.sessions = {}
        self.events = {}
        self.teams = {}
        self.entries = {}
        self.relays = {}

    def __repr__(self) -> str:
        return self.name


def parse_name(name: str):
    m = re.match(r"^(?P<last_name>.*), (?P<first_name>.*) (?P<middle_name>[A-Z])$", name)
    if m is not None:
        return m.groupdict()

    m = re.match(r"^(?P<last_name>.*), (?P<first_name>.*)$", name)
    if m is not None:
        return m.groupdict()

    raise ValueError("Name not properly formatted")   
    

def read(input):
    """Read .cl2 file into Meet object"""
    if type(input) is str:
        lines = input.split("\n")
    elif type(input) is list:
        lines = input
    elif type(input) is bytes:
        lines = input.decode("utf-8").split("\n")

    output = []

    for line in lines:
        code = line[0:2]
        
        if code in RECORD_TYPES.keys():
            output.append(RECORD_TYPES[code](line))
    
    output = tuple(output)

    meetRecord = next(record for record in output if type(record) is MeetRecord)

    meet = Meet()
    meet.name = meetRecord.name

    active_team: Team = None
    active_swimmer: Swimmer = None
    active_entry: IndividualEntry|RelayEntry = None
    splits = None

    for active_record in output:
        
        if type(active_record) is TeamIDRecord:
            active_team = Team(name=active_record.team_name, code=active_record.team_code, lsc=active_record.lsc_code)
            meet.teams[active_team.code] = active_team

        elif type(active_record) is IndividualEventRecord:
            if active_swimmer is None or active_record.swimmer_name != active_swimmer.full_name:
                active_swimmer = Swimmer(full_name=active_record.swimmer_name, age=active_record.swimmer_age, birthdate=active_record.swimmer_birthdate)

                if active_swimmer.id in active_team.swimmers:
                    active_swimmer = active_team.swimmers[active_swimmer.id]
                else:
                    active_team.swimmers[active_swimmer.id] = active_swimmer
            
            active_entry = IndividualEntry()
            active_entry.swimmer = active_swimmer
            active_team.entries.append(active_entry)

            if active_record.event_str in meet.events:
                event = meet.events[active_record.event_str]
            else:
                number = active_record.event_number
                distance = int(active_record.event_distance)
                stroke = STROKES[active_record.event_stroke]
                lower = 0 if active_record.event_lower_age == "UN" else int(active_record.event_lower_age)
                upper = 100 if active_record.event_upper_age == "OV" else int(active_record.event_upper_age)
                age_group = AgeGroup(lower, upper)
                gender = active_record.event_sex.lower()
                event = Event(number, distance, stroke, age_group, gender)
                meet.events[event.number] = event
            active_entry.event = event

            if hasattr(active_record, "seed_time") and active_record.seed_time != "NS" and active_record.seed_time != "DQ":
                if hasattr(active_record, "prelim_heat") and hasattr(active_record, "prelim_lane"):
                    active_entry.seeds["p"] = Seed(time_str=active_record.seed_time, course=active_record.seed_course, heat=active_record.prelim_heat, lane=active_record.prelim_lane)
                elif hasattr(active_record, "final_heat") and hasattr(active_record, "final_lane"):
                    active_entry.seeds["f"] = Seed(time_str=active_record.seed_time, course=active_record.seed_course, heat=active_record.final_heat, lane=active_record.final_lane)  

            if hasattr(active_record, "prelim_time") and active_record.prelim_time != "NS" and active_record.prelim_time != "DQ": 
                active_entry.results["p"] = Result(type="p", rank=active_record.prelim_rank, time_str=active_record.prelim_time, course=active_record.prelim_course)
                if hasattr(active_record, "final_heat") and hasattr(active_record, "final_lane"):
                    if hasattr(active_record, "swimoff_time"):
                        # Small bug here... who won the swimoff? and how do we determine rank?
                        active_entry.seeds["f"] = Seed(time_str=active_record.swimoff_time, rank=active_record.prelim_rank, course=active_record.swimoff_course, heat=active_record.final_heat, lane=active_record.final_lane)       
                    else:
                        active_entry.seeds["f"] = Seed(time_str=active_record.prelim_time, rank=active_record.prelim_rank, course=active_record.prelim_course, heat=active_record.final_heat, lane=active_record.final_lane)       
      
            if hasattr(active_record, "final_time") and active_record.final_time != "NS" and active_record.final_time != "DQ":
                points = active_record.points if hasattr(active_record, "points") else None
                active_entry.results["f"] = Result(type="f", rank=active_record.final_rank, points=points, time_str=active_record.final_time, course=active_record.final_course )

        elif type(active_record) is IndividualInformationRecord:
            if hasattr(active_record, "pref_name"):
                active_swimmer.pref_name = active_record.pref_name

        elif type(active_record) is RelayEventRecord:
            active_entry = RelayEntry()
            active_entry.identifier = active_record.relay_id
            active_team.relays.append(active_entry)

            if active_record.event_str in meet.events:
                event = meet.events[active_record.event_str]
            else:
                number = active_record.event_number
                distance = int(active_record.event_distance)
                stroke = STROKES[active_record.event_stroke]
                lower = 0 if active_record.event_lower_age == "UN" else int(active_record.event_lower_age)
                upper = 100 if active_record.event_upper_age == "OV" else int(active_record.event_upper_age)
                age_group = AgeGroup(lower, upper)
                gender = active_record.event_sex.lower()
                event = Event(number, distance, stroke, age_group, gender)
                meet.events[event.number] = event
            active_entry.event = event
            
            if hasattr(active_record, "seed_time"):
                if hasattr(active_record, "prelim_heat") and hasattr(active_record, "prelim_lane"):
                    active_entry.seeds["p"] = Seed(time_str=active_record.seed_time, course=active_record.seed_course, heat=active_record.prelim_heat, lane=active_record.prelim_lane)
                elif hasattr(active_record, "final_heat") and hasattr(active_record, "final_lane"):
                    active_entry.seeds["f"] = Seed(time_str=active_record.seed_time, course=active_record.seed_course, heat=active_record.final_heat, lane=active_record.final_lane)

            if hasattr(active_record, "prelim_time") and active_record.prelim_time != "NS" and active_record.prelim_time != "DQ":
                active_entry.results["p"] = Result(type="p", rank=active_record.prelim_rank, time_str=active_record.prelim_time, course=active_record.prelim_course)
                # TODO: Add swimoff functionality
                if hasattr(active_record, "final_heat") and hasattr(active_record, "final_lane"):
                    active_entry.seeds["f"] = Seed(time_str=active_record.prelim_time, rank=active_record.prelim_rank, course=active_record.prelim_course, heat=active_record.final_heat, lane=active_record.final_lane)
            
            if hasattr(active_record, "final_time") and active_record.final_time != "NS" and active_record.final_time != "DQ":
                points = active_record.points if hasattr(active_record, "points") else None
                active_entry.results["f"]= Result(type="f", rank=active_record.final_rank, points=points, time_str=active_record.final_time, course=active_record.final_course)

        elif type(active_record) is RelayNameRecord:
            active_swimmer = Swimmer(full_name=active_record.swimmer_name, birthdate=active_record.swimmer_birthdate, age=active_record.swimmer_birthdate)
            if active_swimmer.id in active_team.swimmers:
                active_swimmer = active_team.swimmers[active_swimmer.id]
            
            active_entry.swimmers.append(active_swimmer)
        
        elif type(active_record) is SplitsRecord:
            try:
                splits = active_entry.results[active_record.swim_code.lower()].splits
            except:
                splits = []

            for i in range(min(int(active_record.num_splits) - len(splits), 10)):
                if hasattr(active_record, f"time_{i + 1}"):
                    time = getattr(active_record, f"time_{i + 1}")
                    if active_record.swim_code.lower() in active_entry.results:
                        active_entry.results[active_record.swim_code.lower()].splits.append(Time(time)) 

    return meet

def process_result(cursor, query):
    cursor.execute(query)
    result = cursor.fetchone()
    columns = [column[0] for column in cursor.description]
    return dict(zip(columns, result))

def process_results(cursor, query):
    cursor.execute(query)
    results = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, result)) for result in results]

def create_entry(props, type:Type):
    entry_obj = type()

    if props["ActualSeed_time"] is not None:
        seed_time = Time(int(round(props["ActualSeed_time"]*100)))
        if props["Pre_heat"] != 0:
            entry_obj.seeds["p"] = Seed(time=seed_time, course=props["ActSeed_course"], heat=props["Pre_heat"], lane=props["Pre_lane"])
        elif props["Fin_heat"] != 0:
            entry_obj.seeds["f"] = Seed(time=seed_time, course=props["ActSeed_course"], heat=props["Fin_heat"], lane=props["Fin_lane"])

    if props["Pre_Time"] is not None:
        prelim_time = Time(int(round(props["Pre_Time"]*100)))
        entry_obj.results["p"] = Result(time=prelim_time, type="p", course=props["Pre_course"], rank=props["Pre_place"])
        if props["Pre_heat"] != 0 and props["Fin_heat"] != 0:
            entry_obj.seeds["f"] = Seed(time=prelim_time, course=props["Pre_course"], heat=props["Fin_heat"], lane=props["Fin_lane"])
    
    #TODO: Process DQ information
    if props["Fin_Time"] is not None:
        final_time = Time(int(round(props["Fin_Time"]*100)))
        entry_obj.results["f"] = Result(time=final_time, type="f", course=props["Fin_course"], rank=props["Fin_place"])

    return entry_obj

MDB_STROKES = {
    "A": "Free", 
    "B": "Back",
    "C": "Breast",
    "D": "Fly",
    "E": "Medley",
}

def read_mdb(path):
    if not os.path.isfile(path) or not os.path.splitext(path)[1] == ".mdb":
        return
    
    connection_string = "Driver={Microsoft Access Driver (*.mdb, *.accdb)};Dbq=" + path + ";Uid=Admin;Pwd=TeP69s)lAd_mW-(J_72u"
    connection = connect(connection_string)
    cursor = connection.cursor()

    meet = Meet()

    # Meet
    query = "SELECT Meet_name1, Meet_location, Meet_addr1, Meet_addr2, Meet_city, Meet_state from Meet"
    result = process_result(cursor, query)
    meet.name = result["Meet_name"].rstrip()
    meet.facility = Facility(name=result["Meet_location"], address1=result["Meet_addr1"], city=result["Meet_city"], state=result["Meet_state"], zip=result["Meet_zip"])
    
    # Sessions
    query = "SELECT Sess_no, Sess_name, Sess_starttime, Sess_course FROM Session"
    for result in process_results(cursor, query):
        meet.sessions[result["Sess_no"]] = Session(result["Sess_name"], result["Sess_starttime"], result["Sess_course"])

    # Events
    query = "SELECT Event_no, Event_dist, Event_stroke, Low_age, High_age, Event_gender FROM Event"
    events = process_results(cursor, query)
    for event in events:
        meet.events[event["Event_no"]] = Event(event["Event_no"], event["Event_dist"], MDB_STROKES[event["Event_stroke"]], AgeGroup(int(event["Low_age"]),int(event["High_age"])), event["Event_gender"])

    # Session Events
    query = "SELECT Sess_no, Sess_order, Event_no FROM (Sessitem LEFT JOIN Session ON Sessitem.Sess_ptr = Session.Sess_ptr) LEFT JOIN Event on Sessitem.Event_ptr = Event.Event_ptr"
    for result in process_results(cursor, query):
        meet.sessions[result["Sess_no"]].events[result["Sess_order"]] = meet.events[result["Event_no"]]

    # Teams
    cursor.execute("SELECT Team_name, Team_abbr, Team_lsc from Team")
    teams = cursor.fetchall()
    meet.teams = {team[1].rstrip(): Team(name=team[0].rstrip(), code=team[1].rstrip(), lsc=team[2].rstrip()) for team in teams}

    # Swimmers
    query = "SELECT Team_abbr, Reg_no, Last_name, First_name, Initial, Pref_name FROM Athlete LEFT JOIN Team ON Athlete.Team_no = Team.Team_no"
    swimmers = process_results(cursor, query)
    for swimmer in swimmers:
        full_name = f"{swimmer['Last_name'].rstrip()}, {swimmer['First_name'].rstrip()} {swimmer['Initial'].rstrip()}".rstrip()
        pref_name = swimmer["Pref_name"].rstrip() if swimmer["Pref_name"].rstrip() != "" else None

        meet.teams[swimmer["Team_abbr"].rstrip()].swimmers[swimmer["Reg_no"]] = Swimmer(full_name=full_name, pref_name=pref_name)
    
    # Individual Entries/Results
    query = "SELECT ActualSeed_time, ActSeed_course, Pre_heat, Pre_lane, Pre_Time, Pre_course, Pre_place, Fin_heat, Fin_lane, Fin_Time, Fin_course, Fin_place, Ev_score, Reg_no, Team_abbr, Event_no FROM ((Entry LEFT JOIN Athlete ON Entry.Ath_no = Athlete.Ath_no) LEFT JOIN Team ON Athlete.Team_no = Team.Team_no) LEFT JOIN Event ON Entry.Event_ptr = Event.Event_ptr"
    entries = process_results(cursor, query)
    for props in entries:
        entry = create_entry(props, IndividualEntry)
        entry.event = meet.events[props["Event_no"]]
        entry.swimmer = meet.teams[props["Team_abbr"].rstrip()].swimmers[props["Reg_no"]]

        meet.entries[(props["Event_no"],props["Reg_no"])] = entry

    # Relay Entries/Results
    query = "SELECT ActualSeed_time, ActSeed_course, Pre_heat, Pre_lane, Pre_Time, Pre_course, Pre_place, Fin_heat, Fin_lane, Fin_Time, Fin_course, Fin_place, Ev_score, Team_ltr, Team_abbr, Event_no FROM (Relay Left JOIN Team on Relay.Team_no = Team.Team_no) LEFT JOIN Event on Relay.Event_ptr = Event.Event_ptr"
    relays = process_results(cursor, query)
    for props in relays:
        entry = create_entry(props, RelayEntry)
        entry.event = meet.events[props["Event_no"]]
        entry.identifier = props["Team_ltr"]

        meet.relays[(props["Event_no"],props["Team_abbr"].rstrip(),props["Team_ltr"])] = entry

    # Relay Swimmers
    query = "SELECT Event_no, Team_abbr, RelayNames.Team_ltr, Reg_no, Event_round, Pos_no FROM (((RelayNames LEFT JOIN Relay ON RelayNames.Relay_no=Relay.Relay_no) LEFT JOIN Team ON RelayNames.Team_no = Team.Team_no) LEFT JOIN Athlete ON RelayNames.Ath_no=Athlete.Ath_no) LEFT JOIN Event on RelayNames.Event_ptr=Event.Event_ptr"
    for props in process_results(cursor, query):
        if props["Event_round"].lower() not in meet.relays[(props["Event_no"],props["Team_abbr"].rstrip(),props["Team_ltr"])].swimmers:
            meet.relays[(props["Event_no"],props["Team_abbr"].rstrip(),props["Team_ltr"])].swimmers[props["Event_round"].lower()] = {}
        meet.relays[(props["Event_no"],props["Team_abbr"].rstrip(),props["Team_ltr"])].swimmers[props["Event_round"].lower()][props["Pos_no"]] = meet.teams[props["Team_abbr"].rstrip()].swimmers[props["Reg_no"]]

    # Individual Splits
    query = "SELECT Event_no, Reg_no, Team_abbr, Rnd_ltr, Split_no, Split_Time FROM ((Split LEFT JOIN Athlete ON Split.Ath_no=Athlete.Ath_no) LEFT JOIN Team ON Athlete.Team_no=Team.Team_no) LEFT JOIN Event ON Split.Event_ptr=Event.Event_ptr WHERE Split.Ath_no IS NOT NULL AND Split.Ath_no <> 0"
    splits = process_results(cursor, query)
    for props in splits:
        meet.entries[(props["Event_no"],props["Reg_no"])].results[props["Rnd_ltr"].lower()].splits[props["Split_no"]] = Time(int(round(props["Split_Time"]*100)))

    # Relay Splits
    query = "SELECT Event_no, Team_abbr, Relay.Team_ltr, Rnd_ltr, Split_no, Split_Time FROM ((Split Left Join Relay ON Split.Relay_no=Relay.Relay_no) LEFT JOIN Team on Relay.Team_no=Team.Team_no) LEFT JOIN Event ON Split.Event_ptr=Event.Event_ptr WHERE Split.Relay_no IS NOT NULL AND Split.Relay_no <> 0"
    splits = process_results(cursor, query)
    for props in splits:
        meet.relays[(props["Event_no"],props["Team_abbr"].rstrip(),props["Team_ltr"])].results[props["Rnd_ltr"].lower()].splits[props["Split_no"]] = Time(int(round(props["Split_Time"]*100)))

    return meet


def is_valid_path(path):
    """Validates path to ensure it is valid in the current file system"""

    if not path:
        raise ValueError("No path given")
    if os.path.isfile(path) or os.path.isdir(path):
        return path
    else:
        raise ValueError(f"Invalid path: {path}")

def parse_args():
    """Get command line arguments"""

    parser = argparse.ArgumentParser(description="Options")
    parser.add_argument('-i', '--input_path', dest='input_path', type=is_valid_path, help="The path of the file or folder to process")

    args = vars(parser.parse_args())

    # Display The Command Line Arguments
    print("## Command Arguments #################################################")
    print("\n".join("{}:{}".format(i, j) for i, j in args.items()))
    print("######################################################################")

    return args

def main():

    args = parse_args()

    input_file = args["input_path"]

    if input_file is None:
        input_file = filedialog.askopenfilename()

    if input_file == '':
        exit()

    meet = read_mdb(input_file)

    # f = open(input_file)
    # meet = read(f.readlines())


    # print(meet.teams["FRST"].points)
    # team_scores = [{"team": team, "score": team.points} for team in meet.teams.values()]
    # team_scores.sort(key=lambda x: x["score"], reverse=True)
    print(meet)


if __name__ == "__main__":
    main()