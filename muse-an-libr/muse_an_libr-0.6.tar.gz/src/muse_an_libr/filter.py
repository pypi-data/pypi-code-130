import numpy as np
from scipy.signal import butter, filtfilt
import pandas as pd
from scipy import fftpack

class Filter:
    """
    Filters the dataset based on the needs of the program
    """
    def fft(signal_noise, sec):
        """
        Scipy is used to do FFT and then frequency and amplitude are extracted

        :param signal_noise: signal and noise data
        :type signal_noise: list

        :param sec: secpnds the data was taken for
        :type sec: int

        :return: tuple containing fft signal noise, fft amplitude, fft frequency
        :rtype: tuple 
        """
        time = np.linspace(0, sec, 1000, endpoint=True)
        sig_noise_fft = fftpack.fft(signal_noise)
        sig_noise_amp = 2 / time.size * np.abs(sig_noise_fft)
        sig_noise_freq = np.abs(fftpack.fftfreq(time.size, 3/1000))
        return (sig_noise_fft, sig_noise_amp, sig_noise_freq)

    def amp_calc(sig_noise_amp):
        """
        calculates signal amplitude, taking in fft signal amplitude

        :param sig_noise_amp: amplitude from the fft
        :type sig_noise_amp: fft[1]

        :return: signal_ampltidude
        :rtype: [x, y]
        """
        signal_amplitude = pd.Series(sig_noise_amp).nlargest(2).round(0).astype(int).tolist()
        return signal_amplitude

    
    def freq_calc(sig_noise_fft, sig_noise_freq, sec):
        """
        calculates signal frequency from fft

        :param sig_noise_fft: fft signal noise
        :type sig_noise_fft: fft[0]

        :param sig_noise_freq: fft frequency
        :type sig_noise_freq: fft[2]

        :param sec: secpnds the data was taken for
        :type sec: int

        :return: signal_ampltidude
        :rtype: [x, y]
        """
        magnitudes = abs(sig_noise_fft[np.where(sig_noise_freq >= 0)])
        peak_frequency = np.sort((np.argpartition(magnitudes, -2)[-2:])/sec)
        return peak_frequency

    def butter_lowpass_filter(data, cutoff, fs, order):
        """
        butterworth low pass filter

        :param data: data in the form of a list
        :type data: list created by RandomData.sig_gen function

        :param cutoff: desired cutoff frequency of the filter 
        :type cutoff: int
        
        :param fs: sampling rate in Hz
        :type fs: int
        
        :param order: What order we'd like to use
        :type order: int

        :return: graph
        :rtype: None
        """
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        filtered_signal = filtfilt(b, a,data)
        return filtered_signal
    
    def butter_highpass(cutoff, fs, order=5):
        """
        Implements the highpass filter
        """
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        return b, a

    def butter_highpass_filter(data, cutoff, fs, order=5):
        """
        Implements the highpass filter onto data
        """
        b, a = Filter.butter_highpass(cutoff, fs, order=order)
        y = filtfilt(b, a, data)
        return y