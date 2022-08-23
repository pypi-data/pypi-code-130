import math


class Binomial:
    """
    This class should be used to calculate parameters associated with a binomial distribution.

    :param n_trials: This indicates the number of trails.
    :param p_success: This indicates the probability of success
    """

    def __init__(self, n_trials, p_success):
        self.n_trials = n_trials
        self.p_success = p_success
        self.p_failure = 1 - p_success

    def __repr__(self):
        """
        This function prints out the initialized variables.
        :return None:
        """
        return f"P_success = {self.p_success}, n_trials = {self.n_trials}, p_failure = {self.p_failure}"

    def calculate_mean(self):
        """
        Calculates the mean
        :return mean:
        """
        mean = self.n_trials * self.p_success
        return mean

    def calculate_std(self):
        """
        Calculates the standard deviation
        :return std:
        """
        std = math.sqrt(self.n_trials * self.p_success * self.p_failure)
        return std

    def binomial_distribution_formula(self, expected_success):
        """
        This function calculates the bdf
        :param expected_success: The number of times we expect the outcome to be success
        :return bdf: The binomial distribution function of the expected value
        """
        bdf = math.factorial(self.n_trials) / (math.factorial(expected_success) *
                                               math.factorial(
                                                   self.n_trials - expected_success)
                                               ) * self.p_success ** \
              expected_success * self.p_failure ** self.n_trials - expected_success
        return bdf
