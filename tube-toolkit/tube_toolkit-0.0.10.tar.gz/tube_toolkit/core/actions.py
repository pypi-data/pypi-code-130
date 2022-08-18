from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from typing import Optional, Union
import requests
import json

class Actions():
    def __init__(self, instance):
        self.driver = instance.driver
        self.timeout = 10
        self.driver.implicitly_wait(self.timeout)

    def click(self, by_type: By, by_value: str, timeout: Optional[int] = None) -> Union[str, bool]:
        """
        This method executes a click if the element is found within a time range.

        Arguments:
            by_type: one of the By class constants, you can find them in selenium.webdriver.common.by module.

            by_value: the value of the element to be clicked, for example:
                '//*[@id="element"]' for an element with id='element'
                '//*[@class="element"]' for an element with class='element'

            timeout (Optional): Generates a error if can't locate the element in x seconds. (Standard timeout: 10 seconds).
        """

        try:
            Wait(self.driver, timeout or self.timeout).until(EC.element_to_be_clickable((by_type, by_value))).click()
            return True
        except Exception as e:
            return f"Exception on element {by_value}, {e}"

    def api_post(self, url: str, payload: dict, headers: Optional[dict] = dict({}), verifySSL = True) -> requests.Response:
        '''
        Use this method to send a POST request to any API. 
        Arguments:
            url: The url of the API.
            headers: The headers of the request that will be sent.
                the default headers included in the function are:
                {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            payload: The payload it has to be sent to the API.
            verifySSL: If the SSL certificate should be verified.   (Default: True)
        Returns:
            The response of the API.
        '''

        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json'

        response = requests.post(url, headers=headers, json=payload, verify=verifySSL)
        return response

    def api_get(self, url: str, headers: Optional[dict] = dict({}), verifySSL = True) -> requests.Response:
        '''
        Use this method to send a GET request to any API. 
        Arguments:
            url: The url of the API.
            headers: The headers of the request that will be sent.
                the default headers included in the function are:
                {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            verifySSL: If the SSL certificate should be verified.   (Default: True)
        Returns:
            The response of the API if the request.
        '''

        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json'

        response = requests.get(url, headers=headers, verify=verifySSL)
        return response

    def clear_input(self, by_type: By, by_value: str, timeout: Optional[int] = None) -> Union[str, bool]:
    
        """
        This method executes a clear if the element is found within a time range.

        Arguments:
            by_type: one of the By class constants, you can find them in selenium.webdriver.common.by module.

            by_value: the value of the element to be clicked, for example:
                '//*[@id="element"]' for an element with id='element'
                '//*[@class="element"]' for an element with class='element'

            timeout (Optional): Generates a error if can't locate the element in x seconds. (Standard timeout: 10 seconds).
        """
        
        try:
            Wait(self.driver, timeout or self.timeout).until(EC.presence_of_element_located((by_type, by_value))).clear()
            return True
        except Exception as e:
            return f"Exception on element {by_value}, {e}"

    def send_keys(self, by_type: By, by_value: str, keys_array: list[Union[str, Keys]], timeout: Optional[int] = None) -> Union[str, bool]:

        """
        This method press the keys in the sent array if the element is found within a time range.

        Arguments:
            by_type: one of the By class constants, you can find them in selenium.webdriver.common.by module.

            by_value: the value of the element to be clicked, for example:
                '//*[@id="element"]' for an element with id='element'
                '//*[@class="element"]' for an element with class='element'

            keys_array: the array of keys to be sent to the element, the keys will send in order. For example:
                ['a', 'b', 'c'] for the keys 'a', 'b' and 'c'.
                you can use selenium.webdriver.common.keys module to get the keys too.

            timeout (Optional): Generates a error if can't locate the element in x seconds. (Standard timeout: 10 seconds).
        """

        try:
            Wait(self.driver, timeout or self.timeout).until(EC.visibility_of_element_located((by_type, by_value))).send_keys(keys_array)
            return True
        except Exception as e:
            return f"Exception on element {by_value}, {e}"

    def switch_to_frame(self, by_type: By, by_value: str, timeout: Optional[int] = None) -> Union[str, bool]:

        """
        This method switches to the frame if the element is found within a time range.

        Arguments:
            by_type: one of the By class constants, you can find them in selenium.webdriver.common.by module.

            by_value: the value of the element to be clicked, for example:
                '//*[@id="element"]' for an element with id='element'
                '//*[@class="element"]' for an element with class='element'

            timeout (Optional): Generates a error if can't locate the element in x seconds. (Standard timeout: 10 seconds).
        """

        try:
            Wait(self.driver, timeout or self.timeout).until(EC.frame_to_be_available_and_switch_to_it((by_type, by_value)))
            return True
        except Exception as e:
            return f"Exception on element {by_value}, {e}"
    
    def find_and_get_attribute(self, by_type: By, by_value: str, attribute: str, timeout: Optional[int] = None) -> Union[str, bool]:

        """
        This method finds the element if the element is found within a time range and returns the attribute value.

        Arguments:
            by_type: one of the By class constants, you can find them in selenium.webdriver.common.by module.

            by_value: the value of the element to be clicked, for example:
                '//*[@id="element"]' for an element with id='element'
                '//*[@class="element"]' for an element with class='element'

            attribute: the attribute to be returned. For example:
                'value' for the value attribute.
                'text' for the text attribute.

            timeout (Optional): Generates a error if can't locate the element in x seconds. (Standard timeout: 10 seconds).
        """

        try:
            value = Wait(self.driver, timeout or self.timeout).until(EC.visibility_of_element_located((by_type, by_value))).get_attribute(attribute)
            return value
        except Exception as e:
            return False
    
    def find_element(self, by_type: By, by_value: str, timeout: Optional[int] = None) -> Union[WebElement, bool]:

        """
        This method finds the element if the element is found within a time range and returns the attribute value.

        Arguments:
            by_type: one of the By class constants, you can find them in selenium.webdriver.common.by module.

            by_value: the value of the element to be clicked, for example:
                '//*[@id="element"]' for an element with id='element'
                '//*[@class="element"]' for an element with class='element'

            timeout (Optional): Generates a error if can't locate the element in x seconds. (Standard timeout: 10 seconds).
        """

        try:
            element = Wait(self.driver, timeout or self.timeout).until(EC.visibility_of_element_located((by_type, by_value)))
            return element
        except Exception as e:
            return False