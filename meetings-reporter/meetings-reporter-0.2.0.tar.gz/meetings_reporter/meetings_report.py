import pandas as pd
# import os.path
import os
import logging
from datetime import datetime

from .Meeting import *


logger = logging.getLogger(__name__)


def report(file_path):
    """
    Reporting on meetings' data file

    :param file_path: A valid meetings' data file path
    :return: The corresponding report
    """
    check_path_exists(file_path)
    data = read_meetings(file_path)
    meetings_list = parse_meetings(data)
    meetings_list = filter_working_hours(meetings_list)
    conflicts_list = generate_meetings_conflicts(meetings_list)
    __print_report__(conflicts_list)


def check_path_exists(file_path):
    """
    Check if the file at the given path exists

    :param file_path: A valid file path
    :return: If the file does not exist an error is raised
    """
    if os.path.exists(file_path):
        logger.debug("File {} exists", file_path)
    else:
        logger.error("File does not exist!")
        raise OSError("File not found")


def read_meetings(file_path):
    """
    Reads meetings data from the given file

    :param file_path: A valid file path
    :return: Meetings data in a DataFrame object
    """
    logger.debug("Reading meetings data from file.")
    return pd.read_csv(file_path, header=0)


def filter_working_hours(meetings_list):
    filtered_meetings_list = []
    print ("Working hours: ", meetings_list[0])
    for i in meetings_list[1:]:
        if meetings_list[0].contains(i):
            filtered_meetings_list.append(i)
        else:
            logger.warning("    Meeting %s is outside of working hours. It will be excluded from planning.", i)
    return filtered_meetings_list


def parse_meetings(data):
    """
    Parse meetings information from Strings DataFrame to a Meetings List

    :param data: A meetings Strings data frame
    :return: A Meetings objects list
    """
    logger.debug("Parsing meetings from String DataFrame to Meeting List.")
    meetings_list = []
    for i in range(data.size // 2):
        meetings_list.append(Meeting(datetime.strptime(data['start'][i], '%I:%M%p'),
                                     datetime.strptime(data['end'][i], '%I:%M%p')))
    return meetings_list


def generate_meetings_conflicts(meetings_list):
    """
    Generate a list of conflicting meetings
    :param meetings_list: A list of all meetings
    :return: A list of meeting-pairs conflicting with one another
    """
    logger.debug("Generating meetings conflicts List.")
    conflicts_list = []
    for i in range(len(meetings_list)):
        for j in range(i+1, len(meetings_list)):
            if meetings_list[i].conflicts(meetings_list[j]):
                conflicts_list.append((meetings_list[i], meetings_list[j]))
    return conflicts_list


def __print_report__(conflicts_list):
    print("REPORT: ")
    if len(conflicts_list) == 0:
        print("Planning free from conflicts!")
    else:
        for i in range(len(conflicts_list)):
            print(" Conflict", i+1, ": ", conflicts_list[i][0], " with ", conflicts_list[i][1])
