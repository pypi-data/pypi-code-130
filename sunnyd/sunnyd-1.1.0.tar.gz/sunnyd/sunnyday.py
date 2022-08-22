import requests #, pprint

class Weather:
    """ Creates a weather object getting an apikey as input
    and either a city name or lat and lon coordinates.

    Package use example:
    
    # Create a weather object using a city name:
    # The api key below is not guaranteed to work.
    # Get your own apikey from https://openweathermap.org
    # And wait a couple of hours for the apikey to be activated
    
    >>> weather1 = Weather(apikey = "5960e277b760e0362e9de776f5ba0c8f", city = "Madrid" )
    
    # Using latitude and longitude coordinates
    >>> weather2 = Weather(apikey = "5960e277b760e0362e9de776f5ba0c8f", lat = 41.1, lon = -4.1 )
    
    # get the complete weather data for the next 12 hours:
    >>> weather1.next_12h()
    
    # Simplified data for the next 12 hours:
    >>> weather1.next12h_simplified()
    

    """
    def __init__(self, apikey, city=None, lat=None, lon=None):
        if city and not lat and not lon:
            url = f"https://api.openweathermap.org/data/2.5/forecast?mode=json&q={city}&appid={apikey}&units=metric"
            r = requests.get(url)
            self.data = r.json()
        elif lat and lon and not city:
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={apikey}&units=metric"
            r = requests.get(url)
            self.data = r.json()
        else:
            raise TypeError("Provide either a city or lat and lon arguments")
        if self.data["cod"] != "200":
            raise ValueError(self.data['message'])
            
    def next_12h(self):
        """ Returns 3-hour data for the next 12 hours as a dict
        """
        return self.data['list'][:4]
      
    def next_12h_simplified(self):
        """ Returns date, temperature and sky condition every 3 hours
            for the next 12 hours as a tuple of tuples
        """        
        simple_data = []
        for dicty in self.data['list'][:4]:
           simple_data.append((dicty['dt_txt'], dicty['main']['temp'], dicty['weather'][0]['description']))
        return simple_data

#weather = Weather(apikey = "4860e277b760e0362e9de776f5ba0c7e", city="vienna" )
#print(weather.data)
#weather2 = Weather(apikey = "4860e277b760e0362e9de776f5ba0c7e",  city="Vienna", lon=40.1, lat=3.4 )
#print(weather.data)

#pprint.pprint(weather.next_12h_simplified())  