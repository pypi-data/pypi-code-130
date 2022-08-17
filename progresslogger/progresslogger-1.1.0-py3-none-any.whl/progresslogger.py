'''
Simple Progress Logger for your loops. Replaces built-in enumerate function.
'''


__author__ = 'Michael Genson'
__email__ = 'genson.michael@gmail.com'


from math import floor
import time


def enumerate(sequence, progress_logger=None):
    '''Adds an instance of ProgressLogger to the built-in enumerate function'''
    n = 0

    if type(progress_logger) not in [ProgressLogger, type(None)]:
        raise ValueError(f'progress_logger must be of type {ProgressLogger}, not {type(progress_logger)}')

    if not progress_logger:
        progress_logger = ProgressLogger(sequence, initialize_logger=True)

    else:
        progress_logger.initialize_logger(sequence)

    for elem in sequence:
        try:
            progress_logger.log()

        except Exception as e:
            progress_logger._log_error(e)

        yield n, elem
        n += 1

    progress_logger.log()


class ProgressLogger:
    def __init__(self, sequence=None, initialize_logger=None, silent_errors=True, log_errors_to_console=True,
        show_percentage=True, show_estimate=True, show_next_value=False, percentage_precision=2, give_estimate_in_seconds=False):

        '''Initializes a new instance of ProgressLogger'''
        self.silent_errors = silent_errors
        self.log_errors_to_console = log_errors_to_console

        # only automatically initialize logger if there is a sequence
        if initialize_logger == None:
            initialize_logger = not sequence == None

        if initialize_logger:
            if sequence == None and initialize_logger: raise ValueError('Must provide sequence when initializing logger')
            self.initialize_logger(sequence)

        self.show_percentage = show_percentage
        self.show_estimate = show_estimate
        self.show_next_value = show_next_value
        self.percentage_precision = percentage_precision
        self.give_estimate_in_seconds = give_estimate_in_seconds


    def _log_error(self, error):
        '''Prints error to the console or raises the error depending on initialization params'''
        if not self.silent_errors:
            raise error

        else:
            if self.log_errors_to_console:
                print(error)


    def _calculate_percentage(self):
        '''Calculates percent completion'''
        return round((self.current_iteration/len(self.sequence))*100, self.percentage_precision)


    def _calculate_estimate(self):
        '''Calculates human-readable string of remaining time estimate'''
        seconds = round(self.average_loop_time * ( len(self.sequence) - self.current_iteration ))
        
        # return estimate in seconds
        if self.give_estimate_in_seconds: return f"{seconds} {'seconds' if seconds != 1 else 'second'}"

        # calculate hours and minutes
        days = 0
        hours = 0
        minutes = 0

        if seconds > 60:
            minutes = floor( seconds / 60 )
            seconds = seconds % 60


        if minutes > 60:
            hours = floor( minutes / 60 )
            minutes = minutes % 60


        if hours > 24:
            days = floor ( hours / 24 )
            hours = hours % 24

        estimate_string = ''
        if days: estimate_string += f"{days} {'days' if days != 1 else 'day'}, "
        if hours: estimate_string += f"{hours} {'hours' if hours != 1 else 'hour'}, "
        if minutes: estimate_string += f"{minutes} {'minutes' if minutes != 1 else 'minute'}, "
        if seconds or not estimate_string: estimate_string += f"{seconds} {'seconds' if seconds != 1 else 'second'}, "

        return estimate_string[:-2] # remove trailing comma & space


    def initialize_logger(self, sequence):
        '''Resets counter variables'''
        if sequence == None:
            self._log_error(ValueError('Sequence not provided; unable to initialize progress logger'))
            return

        # the object we're iterating over
        self.sequence = sequence

        # last time self.log() was run
        self.last_loop_timestamp = -1

        # time since last_loop_timestamp
        self.time_since_last_loop = -1
        
        # the current loop counter
        self.current_iteration = -1
        
        # the average time between loops
        self.average_loop_time = -1


    def log(self):
        '''Logs the current loop progress to the console'''

        try:
            self.current_iteration += 1

        except:
            self._log_error(ValueError('Progress logger not initialized; unable to log progress'))
            return

        try:
            # ignore the first iteration
            if self.current_iteration == 0:
                log_string = f"Starting progress logger for {len(self.sequence)} {'items' if len(self.sequence) != 1 else 'item'}."
                if self.show_next_value: log_string += f' Next value: "{self.sequence[self.current_iteration]}".'
                print(log_string)
                
                # initialize start timer
                self.last_loop_timestamp = time.time()
                
                return

            current_time = time.time()

            # update internal timing variables
            self.time_since_last_loop = current_time - self.last_loop_timestamp 
            self.last_loop_timestamp = current_time

            # calculate average by taking the last loop time and weighting it against previous loop times
            self.average_loop_time = ( ( (self.current_iteration - 1) * self.average_loop_time ) + self.time_since_last_loop ) / self.current_iteration

            # final log
            if self.current_iteration == len(self.sequence):
                print(f'Loop complete! Average iteration time: {round(self.average_loop_time, 2)} seconds')
                return

            # build log string
            log_string = f'Iteration {self.current_iteration} of {len(self.sequence)}'
            if self.show_percentage: log_string += f' ({self._calculate_percentage()}%)'
            log_string += ' complete.'
            
            if self.show_estimate: log_string += f' Approximately {self._calculate_estimate()} remaining.'
            if self.show_next_value: log_string += f' Next value: "{self.sequence[self.current_iteration]}".'

            print(log_string)

        except Exception as e:
            self._log_error(e)
            return