from dataclasses import dataclass
import json
from json import JSONDecodeError
import logging
from pathlib import Path
import random
import statistics
import sys
from typing import List, Optional

import click
from pydub import AudioSegment as PydubSegment
from pydub.playback import play
import pyinputplus as pyip
from rich import print

logging.basicConfig(filename="driller.log", level=logging.DEBUG)


@dataclass
class AudioSegment:
    """
    Description of a single drillable segment.
    """

    filename: Path
    start: float
    end: float
    features: List[str]


def drill_everything_once(segments: List[AudioSegment], output_path: str):
    random.shuffle(segments)
    mistakes: List[AudioSegment] = []
    for segment in segments:
        extension = segment.filename.suffix
        if extension == ".mp3":
            full_song = PydubSegment.from_mp3(segment.filename)
            play(full_song[int(segment.start * 1000) : int(segment.end * 1000)])
            for feature in segment.features:
                print(feature)
            answer = pyip.inputYesNo(prompt="Did you get every feature correct?")
            if answer == "no":
                mistakes.append(segment)
        else:
            raise NotImplementedError("Filetype wordt nog niet ondersteund")
    # Would like to use dataclasses_json, but Path poses an issue
    with open(output_path, mode="w") as fh:
        fh.write(
            json.dumps(
                [
                    {
                        "filename": str(mistake.filename),
                        "start": mistake.start,
                        "end": mistake.end,
                        "features": mistake.features,
                    }
                    for mistake in mistakes
                ]
            )
        )


def drill_selectively(
    segments: List[AudioSegment],
    output_path,
    old_mistake_indexes: List[int],
    repetitions_per_old_mistake,
    rights_per_wrong,
):
    previous_attempt_info = [segments[i] for i in old_mistake_indexes]
    previously_correct = [
        s for (i, s) in enumerate(segments) if i not in old_mistake_indexes
    ]
    questions = previous_attempt_info * repetitions_per_old_mistake
    number_of_fillers = rights_per_wrong * len(previous_attempt_info)
    for _ in range(number_of_fillers):
        questions.append(random.choice(previously_correct))
    random.shuffle(questions)
    drill_everything_once(questions, output_path)


def convert_loaded_json_to_segments(loaded_json):
    # TODO: overstappen op https://python-jsonschema.readthedocs.io/en/stable/ ?
    # misschien is er zelfs iets generiek voor dataclasses?
    # er is https://pypi.org/project/dataclasses-json/, maar
    if not isinstance(loaded_json, list):
        raise Exception("Segmentation is not a list")
    for item in loaded_json:
        if not isinstance(item, dict):
            raise Exception("List item is not a dictionary")
        if set(item.keys()) != set(["filename", "start", "end", "features"]):
            raise Exception("List item has incorrect property set")
        if (
            not isinstance(item["filename"], str)
            or not isinstance(item["start"], float)
            or not isinstance(item["end"], float)
            or not isinstance(item["features"], list)
        ):
            raise Exception("Incorrectly typed property")
        if not all([isinstance(feature, str) for feature in item["features"]]):
            raise Exception("Incorrectly typed feature")
        path = Path(item["filename"])
        path.resolve(True)
    return [
        AudioSegment(Path(path), item["start"], item["end"], item["features"])
        for item in loaded_json
    ]


@click.command()
@click.argument("segment_info")  # staat op string, maar is een file path...
@click.argument("output_path")  # staat op string, maar is een file path...
@click.option(
    "-p",
    "--previous-attempt-info",
    required=False,
    help="Output that was generated after a previous attempt for the same task. Only used in conjunction with -t and -r.",
)  # type nodig
@click.option(
    "-r",
    "--repetitions_per_old_mistake",
    required=False,
    type=int,
    help="How many times a segment that contained a mistake last time should be repeated. Only used in conjunction with -p and -t.",
)
@click.option(
    "-w",
    "--rights_per_wrong",
    type=int,
    required=False,
    help="How many segments that were previously identified correctly should be used per segment that was wrong last time.",
)
def drill(
    segment_info: str,
    output_path: str,
    previous_attempt_info: str,
    repetitions_per_old_mistake: Optional[int],
    rights_per_wrong: Optional[int],
):
    optional_parameter_absent = [
        x is None
        for x in (previous_attempt_info, rights_per_wrong, repetitions_per_old_mistake)
    ]
    if any(optional_parameter_absent) and not all(optional_parameter_absent):
        print(f"[bold red]Optional parameters are specified as a group.[/bold red]")
        sys.exit(0)
    try:
        with open(segment_info) as fh:
            json_segments = json.load(fh)
            segments: List[AudioSegment] = convert_loaded_json_to_segments(
                json_segments
            )
    except Exception as e:
        print(f"[bold red]Unable to load segments.[/bold red]")
        if isinstance(e, TypeError):
            print(
                f"[bold red]Does the segmentation file follow the specified format?[/bold red]"
            )
        elif isinstance(e, IOError):
            print(
                f"[bold red]Is the segmentation file readable by the program?[/bold red]"
            )
        logging.error(e)
        print(f"[bold red]Check the logs for more info.[/bold red]")
        sys.exit(1)
    assert all(optional_parameter_absent) or not any(optional_parameter_absent)
    if all(optional_parameter_absent):
        drill_everything_once(segments, output_path)
    elif not any(optional_parameter_absent):
        try:
            with open(previous_attempt_info) as fh:
                old_mistake_indexes: List[int] = json.load(fh)
            drill_selectively(
                segments,
                output_path,
                old_mistake_indexes,
                repetitions_per_old_mistake,
                rights_per_wrong,
            )
        except Exception as e:
            print(f"[bold red]Unable to load previous attempt info.[/bold red]")
            if isinstance(e, IOError):
                print(
                    f"[bold red]Is the file with info on the previous attempt readable by the program?[/bold red]"
                )
            logging.error(e)
            print(f"[bold red]Check the logs for more info.[/bold red]")
            sys.exit(1)


if __name__ == "__main__":
    drill()
