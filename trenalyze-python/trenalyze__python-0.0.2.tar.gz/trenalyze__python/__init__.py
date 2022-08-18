# Importing the requests module.
import requests

# Importing the CaseInsensitiveDict class from the requests.structures module.
from requests.structures import CaseInsensitiveDict

# Importing the json module.
import json

# The class is used to send whatsApp messages to a phone number using the Trenalyze API
class Trenalyze:

    def __init__(self):
        """
        A constructor.
        """

        # `pass` is a null statement. It is used as a placeholder.
        pass

    def setToken(self, token):
        """
        It sets the token for the user.
        
        :param token: The token of the sender you want to use
        """

       # Setting the token for the user.
        self.token = token
    
    def setSender(self, sender):
        """
        It sets the sender of the message.
        
        :param sender: The sender's phone number.
        """

        # Setting the sender of the message.
        self.sender = sender

    def setReceiver(self, receiver):
        """
        It sets the receiver of the message.
        
        :param receiver: The WhatsApp Number of the receiver
        """

        # Setting the receiver of the message.
        self.receiver = receiver
    
    def setMsgtext(self, msgtext):
        """
        It sets the message text.
        
        :param msgtext: The text of the message
        """

        # Setting the message text.
        self.msgtext = msgtext

    def setDebug(self, debug = False):
        """
        It sets the debug flag to True or False.
        
        :param debug: If True, the debug mode is enabled, defaults to False (optional)
        """

        # Setting the debug flag to True or False.
        self.debug = debug

    def __getUrl(self):
        """
        It returns the url of the Trenalyze API.
        """

        # Setting the url of the Trenalyze API.
        url = "https://trenalyze.com/api/send"

        # Returning the url of the Trenalyze API.
        return url

    def __sendRequest(self):
        """
        It sends a request.
        """

        # Sending a request to the Trenalyze API.
        try:

           # Creating a case insensitive dictionary.
            headers = CaseInsensitiveDict()

           # Setting the content type of the request to json.
            headers['Content-Type'] = 'application/json'

           # Setting the url of the Trenalyze API.
            url = self.__getUrl()

            # Creating a dictionary with the keys sender, token, receiver and msgtext.
            data = {
                "sender": self.sender,
                "token": self.token,
                "receiver": self.receiver,
                "msgtext": self.msgtext
            }
            
            # Sending a post request to the Trenalyze API.
            resp = requests.post(url = self.__getUrl(), data=json.dumps(data), headers=headers)

           # Checking if the request was successful.
            if resp.status_code == 200:

                # Returning the response of the request in json format.
                return resp.json()

            # Checking if the request was successful. If it was successful, it returns the response of
            # the request in json format. If it was not successful, it returns an error message.
            else:

                # Checking if the debug flag is set to True.
                if self.debug == True:

                    # Returning an error message.
                    return "Error: {}".format(resp.status_code)

               # Returning an error message if the request was not successful.
                else:

                    # Returning an error message if the request was not successful.
                    return "Sorry an Error Occured. Kindly enable debug mode to see more details"

       # Catching any exception that might occur and returning an error message.
        except Exception as e:

           # It checks if the debug flag is set to True.
            if self.debug == True:

                # Returning an error message.
                return "Error: {}".format(e)

           # It returns an error message if the request was not successful.
            else:

                # Returning an error message if the request was not successful.
                return "Sorry an Error Occured. Kindly enable debug mode to see more details"

    def sendMessage(self):
        """
        If the sender is empty, return "Sender cannot be empty". If the receiver is empty, return
        "Receiver cannot be empty". If the sender is not a number, return "Sender must me a valid Phone
        Number". If the receiver is not a number, return "Receiver must me a valid Phone Number". If the
        token is empty, return "Token is Required". If the token length is less than 20, return "Invalid
        Token. Kindly Re Confirm Token". Otherwise, return the result of the __sendRequest() function
        :return: The return value is the result of the __sendRequest() method.
        """

        #make sure sender and receiver are numbers and its not empty
        if self.sender == "":
            return "Sender cannot be empty"

        #if receiver is empty
        if self.receiver == "":
            return "Receiver cannot be empty"

        #if sender is not a number
        if not self.sender.isdigit():
            return "Sender must me a valid Phone Number"

        #if receiver is not a number
        if not self.receiver.isdigit():
            return "Receiver must me a valid Phone Number"

        #if token is empty
        if self.token == "":
            return "Token is Required"

        #if token length is less than 20 or greater than 20
        if len(self.token) < 20 or len(self.token) > 20:
            return "Invalid Token. Kindly Re Confirm Token"
            
        # Returning the result of the __sendRequest() method.
        return self.__sendRequest()

