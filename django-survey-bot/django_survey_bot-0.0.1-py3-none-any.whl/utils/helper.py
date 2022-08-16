import uuid
from survey_bot.utils.exception_handler import ExceptionHandler
from survey_bot.utils.logs import Logs
from bs4 import BeautifulSoup

class UtilityHelper:
    def __init__(self):
        """Initializes UtilityHelper class."""
        self.__log = Logs()
        self.__exception = ExceptionHandler()
        
    def get_uuid(self):
        return str(uuid.uuid4())

    def get_client_ip(self, request):
        ip = None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', None)
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', None)
        return ip
    
    def get_browser_type(self, request):
        try:
            return request.META['HTTP_USER_AGENT']
        except:
            return None
    
    def remove_html_tags(self,text):
        """Remove html tags from a string"""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

    def remove_empty_html_tags(self,html_object):
        soup = BeautifulSoup(html_object,'html.parser')
        for x in soup.find_all():
            if len(x.get_text(strip=True)) == 0 and x.name not in ['br', 'img']:
                x.extract()
        return str(soup)
