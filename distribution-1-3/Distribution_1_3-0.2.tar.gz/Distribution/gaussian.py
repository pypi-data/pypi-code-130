from math import sqrt, pi, e
import matplotlib.pyplot as plt
import numpy as np


class Gaussian:
    """
    This class will be used to calculate different parameter associated with the gaussian distribution
    :param data: The continuous distribution (list or n.array) .


    salary (float)
    """

    def __init__(self, data: float):
        """
        This function initializes the variables hence making them available for every function under this class.
        The data will be converted into a numpy array to improve speed and calculation efficiency.
        The standard deviation and the mean are also calculated and stored.
        """
        self.data = np.array(data)
        self.mean = self.data.mean()
        self.std = self.data.std()

    def __repr__(self):
        """
        This function displays the mean and the standard deviation of any given distribution
        :return None:
        """
        print(f"The data distribution has a mean of {self.mean} and a standard deviation of {self.std}")

    def get_std(self):
        """
        This function returns the standard deviation of the distribution
        :return std: The standard deviation of the distribution (np.array)
        """
        std = self.std
        return std

    def get_mean(self):
        """
        This function returns the mean of the distribution
        :return mean: The mean of the distribution (np.array)
        """
        mean = self.mean
        return mean

    def plot_histogram(self):
        """
        :return: A histogram plot of the gaussian distribution:
        """
        plt.hist(self.data)
        plt.title("An histogram plot of the data", font_size=19)
        plt.xlabel("The Values", font_size=16)
        plt.ylabel("Counts", font_size=16)
        plt.show()

    def calculate_pdf(self, obs):
        """
        This function calculates the probability distribution function of an observation
        :param obs: The number of which its probability distribution function is required (int)
        :return pdf: The calculated pdf of the obs (float)
        """
        pdf = round((1 / (self.std * sqrt(2 * pi))) *
                    (e ** -0.5 * ((obs - self.mean) / self.std) ** 2), 2)
        return pdf
