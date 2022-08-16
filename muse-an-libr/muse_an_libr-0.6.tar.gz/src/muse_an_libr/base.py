class Validate:
    """
    Validates if the dataset is in correct format.

    :param inpt: The input
    :type inpt: [[x, [y,z]],[x, [y,z]]]
    """
    
    def __init__(self, inpt):
        self.inpt = inpt
    
    def Valid(museInput):
        """
        Checks to see if the inpt is in the valid format

        :param museInput: Output from the muse headset
        :type museInput: [[x, [y,z]],[x, [y,z]]]

        :return: if the input is valid or not
        :rtype: boolean
        """
        val = True

        for i in range(len(museInput)):
            if len(museInput[i]) != 2 or len(museInput[i][1]) != 5:
                val = False
        
        return val

    def TimeStamp(museInput):
        """
        Returns the timestamps of the data

        :param museInput: Output from the muse headset
        :type museInput: [[x, [y,z]],[x, [y,z]]]

        :return: list of the timestamps
        :rtype: list
        """
        lst = []
        
        for i in range(len(museInput)):
            lst.append(museInput[i][0])

        return lst 
    
    def Values(museInput):
        """
        Returns the timestamps of the data

        :param museInput: Output from the muse headset
        :type museInput: [[x, [y,z]],[x, [y,z]]]

        :return: list of the values
        :rtype: list
        """
        lst = []
        
        for i in range(len(museInput)):
            lst.append(museInput[i][1])

        return lst 

    def ValuesSpecific(museInput, channel):
        """
        Returns the timestamps of the data

        :param museInput: Output from the muse headset
        :type museInput: [[x, [y,z]],[x, [y,z]]]
        
        :param channel: Which channels to use, index 0
        :type channel: lst

        :return: list of the values
        :rtype: list
        """
        lst = []
        
        for i in range(len(museInput)):
            x_lst = []
            for cnl in channel:
                x_lst.append(museInput[i][1][cnl])
            lst.append(x_lst)


        return lst 