import matplotlib.pyplot as plt

class Visualize:
    """
    Allows you to visualize the data
    """
    def plot_rand(data):
        """
        Designed to allow you to visualize and plot the random graph
        
        :param data: data in the form of a list
        :type data: list created by RandomData.sig_gen function

        :return: graph
        :rtype: None
        """
        plt.plot(data)
        plt.show()
        return