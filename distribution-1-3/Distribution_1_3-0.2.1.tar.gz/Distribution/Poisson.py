import math


class Poisson:

    def __init__(self, mean, expected_outcome):
        self.mean = mean
        self.expected_outcome = expected_outcome

    def pmf(self):
        mass_function = (math.e ** self.mean * self.mean ** self.expected_outcome) / \
                        math.factorial(self.expected_outcome)
        return mass_function
