import numpy as np

class PeTeR:
  """
  Instantiate a PeTeR operation.
  PeTeR will describe the given number.
  """

  def says(self, num):
    """
    Get numbers described by Mr. PeTeR

    :param num: The number
    :type num: int

    :return: PeTeR's message.
    :rtype: str
    """

    message = ""
    if(np.remainder(num,2) == 0):
      message = "PeTeR says the number you gave is even."
    else:
      message = "PeTeR says the number you gave is odd."

    if(num == 69):
      message += "\nPeTeR says nice."
    return message