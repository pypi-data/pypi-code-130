from numpy import random
import numpy as np


class RandomData:
    """
    Allows you to generate random datasets
    """

    def sample_muse(length):
        """
        Create sample muse data with no timestamp

        :param length: Length of the dataset
        :type length: int

        :return: list of length length with desired number of channels
        :rtype: list in list
        """

        return (random.rand(length, 5) * 80).tolist()

    def sample_muse_channels(length, channels):
        """
        Create sample muse data with no timestamp and lets you choose the number of channels you want

        :param length: Length of the dataset
        :type length: int
        
        :param channels: Amount of desired channels
        :type channels: int

        :return: list of length length with desired number of channels
        :rtype: list in list
        """
        return (random.rand(length, channels) * 80).tolist()
    
    def sample_muse_time(length, channels):
        """
        Create sample muse data with timestamp and lets you choose the number of channels you want

        :param length: Length of the dataset
        :type length: int
        
        :param channels: Amount of desired channels 
        :type channels: int

        :return: list of length length with desired number of channels
        :rtype: list in list with timestamps
        """
        result = []
        for i in range(length):
            ap = [i+1, (random.rand(1, channels) * 80).tolist()]
            result.append(ap)
        return result
    
    def sig_gen(sec, sig_freq, sig_amp, noise_freq, noise_amp):
        time = np.linspace(0, sec, 1000, endpoint=True)

        signal = sig_amp*np.sin(2*np.pi*sig_freq*time)
        noise = noise_amp*np.sin(2*np.pi*noise_freq*time)

        signal_noise = signal + noise

        return signal_noise