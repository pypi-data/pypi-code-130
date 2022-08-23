import math


class Bernoulli:
    """
    This class will be used to calculate different parameter associated with the bernoulli distribution
    :param p: Probability of success (float)
    """

    def __init__(self, p: float):
        self.p = p
        self.mean = p
        # Probability of failure(q) is the same as 1 - probability of success; since they must both add up to 1
        self.q = 1 - p

    def __repr__(self):
        """
        This function prints out the probability of success and the probability of failure
        :return None:
        """
        print(f"Probability of success(p) = mean = {self.mean}, probability of failure = {self.q}")

    def get_std(self):
        """
        This function calculates and returns the standard deviation of the distribution
        :return std: Standard Deviation(float)
        """
        std = math.sqrt(self.q * self.p)
        return std

    def get_pdf(self, success: bool = True):
        """
        This function calculates the probability density function of the distribution for either success or failure
        :param success: Indicate whether the calculation is for success or failure; with 'true' indicating success and
        'false' indicating failure
        :return pdf: probability density function (float)
        """
        if success:
            x = 1
        else:
            x = 0

        pdf = round(self.p ** x * self.q ** (1 - x), 2)
        return pdf
