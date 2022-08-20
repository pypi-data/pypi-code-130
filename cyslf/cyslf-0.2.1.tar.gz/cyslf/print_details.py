import argparse

from cyslf.models import League
from cyslf.validation import validate_file

parser = argparse.ArgumentParser(description="Print current team details")
parser.add_argument(
    "--input_player_csv",
    "-i",
    type=str,
    help="input player csv. eg 'boys34-players.csv'",
)
parser.add_argument(
    "--team_csv",
    "-t",
    type=str,
    help="team csv. should contain team information (name, location, etc)",
)

def main():
    args = parser.parse_args()
    validate_file(args.input_player_csv)
    validate_file(args.team_csv)

    league = League.from_csvs(args.input_player_csv, args.team_csv)
    league.details()
