import logging


logger = logging.getLogger(__name__)


class Meeting:
    """
    Simple meeting
    """

    def __init__(self, start_time, end_time):
        """
        Create a Meeting

        :param start_time: The starting time
        :param end_time: The ending time
        """
        if start_time >= end_time:
            logging.warning("Meeting " + self + "is incoherent, report can include mistakes.")
        self.start = start_time
        self.end = end_time

    def __str__(self):
        return self.start.strftime('%I:%M%p') + "--->" + self.end.strftime('%I:%M%p')

    def __repr__(self):
        return self.start.strftime('%I:%M%p') + "--->" + self.end.strftime('%I:%M%p')

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end

    def __ne__(self, other):
        return not self.__eq__(other)

    def conflicts(self, other):
        return not (self.start >= other.end or self.end <= other.start)

    def contains(self, other):
        return self.start <= other.start and self.end >= other.end
