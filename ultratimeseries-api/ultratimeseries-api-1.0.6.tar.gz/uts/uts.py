from uts import httpHandler
from uts import utils
from uts import authentication

class UTS(object):
    url = ''
    host = ''
    auth = None

    def __init__(self, url='http://localhost:8080',host='localhost'):
        self.url = url
        self.host = host
        self.auth = authentication.Authentication()

    class Actors(object):
        actors = []

        def __init__(self):
            self.actors = []
        
        def addActor(self,key):
            self.actors.append(utils.actorRequestBody(key))
        def clearActors(self):
            self.actors = []

    class Messages(object):
        messages = []

        def __init__(self):
            self.messages = []

        def addMessage(self,subject,action,measure,value,date=""):
            self.messages.append(utils.messageCreateBody(subject,action,measure,value,date))

        def clearMessages(self):
            self.messages = []

    class Role(object):

        key = ''
        properties = []

        def __init__(self,key):
            self.key = key
            self.properties = []

        def addProperties(self,properties):
            for prop in properties:
                self.properties.append(utils.roleProperty(prop[0],prop[1]))

        def clearProperties(self):
            self.properties= []

        def updateKey(self,key):
            self.key = key

    class ActorRole(object):

        roleKey  = ''
        actorKey = ''

        properties = []
        
        def __init__(self,roleKey='',actorKey=''):
            self.roleKey = roleKey
            self.actorKey = actorKey
            self.properties = []

        def addProperties(self,properties):
            for prop in properties:
                self.properties.append(utils.rolePropertySetValue(prop[0],prop[1]))

        def clearProperties(self):
            self.properties= []

        def updateActorKey(self,actorKey):
            self.actorKey = actorKey

        def updateRoleKey(self,roleKey):
            self.roleKey = roleKey


    def login(self,apikey):
        """
        This function authenticates the user

        Args:
            apikey:    Authentication credential granted by the service provider 
        Example:
            >>> login("MyApiKey")
        """
        self.auth.login(apikey,self.host,self.url)
    
    #Actor related requests

    def actorCreate(self,actors):
        """
        This function inserts an array of actors in the database

        Args:
            actors:    An array of Actor bodies
        Returns:
            A String indicating the result of the operation, an empty String is returned in case of success
        Example:
            >>> actors = actors() \n
            >>> actors.addActor("CristianoRonaldo") \n
            >>> //add as much messages as your HTTP Post buffer can handle\n
            >>> actorCreate(actors)
        """
        return httpHandler.post(self.url,'/api/actor/create',self.host,actors.actors,self.auth.token)

    def actorExists(self,key):
        """
        This function checks if a user exists in the database

        Args:
            key:    Actor's unique identifier
        Returns:
            A String representation of a JSON object indicating the actor's key and the date it was created, "Invalid Request" if the actor doesn't exist
        Example:
            >>> print(actorExists("CristianoRonaldo"))\n
            >>> "{ key: "CristianoRonaldo", "created":"2021-07-09T16:47:36Z"}"
        """
        return httpHandler.get(self.url,'/api/actor/exist',self.host,utils.actorGetBody(key),self.auth.token)

    def actorContains(self,key):
        """
        This function checks if there are Actors that contain a given String in their key

        Args:
            key:    Actor's unique identifier
        Returns:
            A String representation of an array of JSON objects indicating the actor's key and the date it was created, "Invalid Request" if the actor doesn't exist
        Example:
            >>> print(actorContains("Ronaldo"))\n
            >>> "[{ key: "CristianoRonaldo", "created":"2021-07-09T16:47:36Z"},{ key: "RonaldoNazário", "created":"2021-07-09T16:47:36Z"}]" \n
            >>> \n
            >>> print(actorContains("Cristiano"))\n
            >>> "[{ key: "CristianoRonaldo", "created":"2021-07-09T16:47:36Z"}]"
        """
        return httpHandler.get(self.url,'/api/actor/contains',self.host,utils.actorGetBody(key),self.auth.token)

    def actorCount(self):
        """
        This function returns the amount of Actors in the database

        Returns:
            An Integer that represents the amount of Actors present in the database
        Example:
            >>> Print(actorCount())\n
            >>> 2
        """
        return int(httpHandler.get(self.url,'/api/actor/count',self.host,"",self.auth.token))

    def actorAll(self):
        """
        This function returns a list containing every Actor present in the database

        Returns:
            A String representation of an array of JSON objects indicating the actor's key and the date it was created
        Example:
            >>> print(actorAll())\n
            >>> "[{ key: "CristianoRonaldo", "created":"2021-07-09T16:47:36Z"},{ key: "RonaldoNazário", "created":"2021-07-09T16:47:36Z"}]"
        """
        return httpHandler.get(self.url,'/api/actor',self.host,"",self.auth.token)

    def actorProperties(self,key):
        """
        This function returns a list of all properties associated to an actor
        Args:
            key:    Actor's unique identifier
        Returns:
            A String representation of an array of JSON objects indicating the property name and it's value
        Example:
            >>> print(actorProperties("CristianoRonaldo"))\n
            >>> "[{"Property":"PositionInText","Value":"Striker"}]" \n
        """
        return httpHandler.get(self.url,'/api/actor/actorproperties',self.host,utils.actorGetBody(key),self.auth.token)

    def actorRoles(self,key):
        """
        This function returns a list of all Roles associated to an actor
        Args:
            key:    Actor's unique identifier
        Returns:
            A String representation of an array of JSON objects indicating the property name and it's value
        Example:
            >>> print(actorRoles("CristianoRonaldo"))\n
            >>> "[{"role":"Position"}]" \n
        """
        return httpHandler.get(self.url,'/api/actor/actorroles',self.host,utils.actorGetBody(key),self.auth.token)

    def actorMessagesSent(self,key):
        """
        This function returns the amount of Messages sent by a given Actor

        Returns:
            An Integer that represents the amount of Messages sent by a given Actor
        Example:
            >>> Print(actorMessagesSent("CristianoRonaldo"))\n
            >>> 1
        """
        return httpHandler.get(self.url,'/api/actor/messagessent',self.host,utils.actorGetBody(key),self.auth.token)

    def actorSharingRolesWith(self,key):
        """
        This function returns a list of all Actors that share atleast a Role with a given actor
        Args:
            key:    Actor's unique identifier
        Returns:
            A String representation of an array of JSON objects indicating the Actor key and it's creation date
        Example:
            >>> print(actorSharingRolesWith("CristianoRonaldo"))\n
            >>> "[{ key: "RonaldoNazário", "created":"2021-07-09T16:47:36Z"}]" \n
        """
        return httpHandler.get(self.url,'/api/actor/sharingroleswith',self.host,utils.actorGetBody(key),self.auth.token)

    def actorSharingActionsWith(self,key):
        """
        This function returns a list of all Actors that share atleast an Action with a given actor
        Args:
            key:    Actor's unique identifier
        Returns:
            A String representation of an array of JSON objects indicating the Actor key and it's creation date
        Example:
            >>> print(actorSharingActionsWith("CristianoRonaldo"))\n
            >>> "[{ key: "RonaldoNazário", "created":"2021-07-09T16:47:36Z"}]" \n
        """
        return httpHandler.get(self.url,'/api/actor/sharingactionswith',self.host,utils.actorGetBody(key),self.auth.token)

    #Message related requests

    def getAllUnits(self):
        """
        This function returns a list with every unit suported by UTS

        Returns:
            A String representation of an array of JSON objects indicating the unit and the respective measure
        Example:
            >>> print(getAllUnits())\n
            >>> "[ ... , {"dimension": {"id": 28,"name": "Length"},"unit": {"id": 27675,"name": "Meter"}}, ...]"
        """
        return httpHandler.get(self.url,'/api/units',self.host,"",self.auth.token)

    def getAllTimewindows(self):
        """
        This function returns a list with every timewindow suported by UTS

        Returns:
            A String representation of a JSON object indicating the timewindows
        Example:
            >>> print(getAllTimewindows())\n
            >>> {"day":1,"dayOfWeek":2,"month":3,"year":4,"hour":5}
        """
        return httpHandler.get(self.url,'/api/time-window',self.host,"",self.auth.token)

    def messageCreate(self,messages):
        """
        This function inserts an array of messages into the database

        Args:
            messages:    An array of Message bodies
        Returns:
            An empty String in case of success
        Example:
            >>> messages = Messages()\n
            >>> messages.addMessage("CristianoRonaldo","DistanceCovered",LengthMeter(),11587.27,"2021-07-09T16:47:36Z")\n
            >>> # can add as much messages as your HTTP Post buffer can handle\n
            >>> messageCreate(messages)
        """
        return httpHandler.post(self.url,'/api/messages/create',self.host,messages.messages,self.auth.token)

    def getAllMessages(self):
        """
        This function returns all the existing time series present in the database. A time series is a unique combination of Action and Subject

        Returns:
            A String representation of an array of JSON objects indicating the existing time series
        Example:
            >>> print(getAllMessages())\n
            >>> [{"action": "DistanceCovered","subject": "RonaldoNazário","dimension": "Length","preferedUnit": "Meter","created": "2021-07-09T16:47:36Z"}]
        """
        return httpHandler.get(self.url,'/api/messages/all',self.host,"",self.auth.token)

    def getMaxMessage(self,subject,action,start=None,end=None,measure=None):
        """
        This function returns the max value registered for a certain Action, Subject and period

        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            start:  the lower end of the time period to be evaluated (optional)
            end:    the upper end of the time period to be evaluated (optional)
            measure:      The unit of measurement which the value should be displayed (optional)
        Returns:
            A float
        Example:
            >>> print(getMaxMessage("CristianoRonaldo","DistanceCovered"))\n
            >>> 11587.27
        """
        return float(httpHandler.get(self.url,'/api/messages/max',self.host,utils.messageQueryBody(subject,action,start,end,measure),self.auth.token))

    def getMinMessage(self,subject,action,start=None,end=None,measure=None):
        """
        This function returns the min value registered for a certain Action, Subject and period

        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            start:  the lower end of the time period to be evaluated (optional)
            end:    the upper end of the time period to be evaluated (optional)
            measure:      The unit of measurement which the value should be displayed (optional)
        Returns:
            A Decimal
        Example:
            >>> print(getMinMessage("CristianoRonaldo","DistanceCovered"))\n
            >>> 11587.27
        """
        return float(httpHandler.get(self.url,'/api/messages/min',self.host,utils.messageQueryBody(subject,action,start,end,measure),self.auth.token))

    def getFirstMessage(self,subject,action,start=None,end=None):
        """
        This function returns the first value registered for a certain Action, Subject and period

        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            start:  the lower end of the time period to be evaluated (optional)
            end:    the upper end of the time period to be evaluated (optional)
        Returns:
            A String representation of a JSON object
        Example:
            >>> print(getFirstMessage("CristianoRonaldo","DistanceCovered"))\n
            >>> {"date": "2021-07-09T16:47:36Z","value": 11587.27,"created": "2021-07-09T16:47:36Z"}
        """
        return httpHandler.get(self.url,'/api/messages/first',self.host,utils.messageQueryBody(subject,action,start,end),self.auth.token)

    def getLastMessage(self,subject,action,start=None,end=None):
        """
        This function returns the last value registered for a certain Action, Subject and period

        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            start:  the lower end of the time period to be evaluated (optional)
            end:    the upper end of the time period to be evaluated (optional)
        Returns:
            A String representation of a JSON object
        Example:
            >>> print(getLastMessage("CristianoRonaldo","DistanceCovered"))\n
            >>> {"date": "2021-07-09T16:47:36Z","value": 11587.27,"created": "2021-07-09T16:47:36Z"}
        """
        return httpHandler.get(self.url,'/api/messages/last',self.host,utils.messageQueryBody(subject,action,start,end),self.auth.token)

    def getMessageCount(self,subject,action,start=None,end=None):
        """
        This function returns the amount of messages present in the database for a certain Action, Subject and period

        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            start:  the lower end of the time period to be evaluated (optional)
            end:    the upper end of the time period to be evaluated (optional)
        Returns:
            An Integer
        Example:
            >>> print(getMessageCount("CristianoRonaldo","DistanceCovered"))\n
            >>> 1
        """
        return int(httpHandler.get(self.url,'/api/messages/count',self.host,utils.messageQueryBody(subject,action,start,end),self.auth.token))

    def getMessageSum(self,subject,action,start=None,end=None,measure=None):
        """
        This function returns the sum of the values from the messages present in the database for a certain Action, Subject and period

        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            start:  the lower end of the time period to be evaluated (optional)
            end:    the upper end of the time period to be evaluated (optional)
            measure:      The unit of measurement which the value should be displayed (optional)
        Returns:
            A Decimal
        Example:
            >>> print(getMessageSum("CristianoRonaldo","DistanceCovered"))\n
            >>> 11587.27
        """
        return httpHandler.get(self.url,'/api/messages/sum',self.host,utils.messageQueryBody(subject,action,start,end,measure),self.auth.token)

    def getMessageAverage(self,subject,action,start=None,end=None,measure=None):
        """
        This function returns the average value from the messages present in the database for a certain Action, Subject and period

        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            start:  the lower end of the time period to be evaluated (optional)
            end:    the upper end of the time period to be evaluated (optional)
            measure:      The unit of measurement which the value should be displayed (optional)
        Returns:
            A Decimal
        Example:
            >>> print(getMessageAverage("CristianoRonaldo","DistanceCovered"))\n
            >>> 11587.27
        """
        return httpHandler.get(self.url,'/api/messages/avg',self.host,utils.messageQueryBody(subject,action,start,end,measure),self.auth.token)

    def getMessageMedian(self,subject,action,start=None,end=None,measure=None):
        """
        This function returns the median value from the messages present in the database for a certain Action, Subject and period

        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            start:  the lower end of the time period to be evaluated (optional)
            end:    the upper end of the time period to be evaluated (optional)
            measure:      The unit of measurement which the value should be displayed (optional)
        Returns:
            A Decimal
        Example:
            >>> print(getMessageMedian("CristianoRonaldo","DistanceCovered"))\n
            >>> 11587.27
        """
        return httpHandler.get(self.url,'/api/messages/med',self.host,utils.messageQueryBody(subject,action,start,end,measure),self.auth.token)

    def getMessageMode(self,subject,action,start=None,end=None,measure=None):
        """
        This function returns the mode from the messages present in the database for a certain Action, Subject and period

        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            start:  the lower end of the time period to be evaluated (optional)
            end:    the upper end of the time period to be evaluated (optional)
            measure:      The unit of measurement which the value should be displayed (optional)
        Returns:
            A Decimal
        Example:
            >>> print(getMessageMode("CristianoRonaldo","DistanceCovered"))\n
            >>> 11587.27
        """
        return httpHandler.get(self.url,'/api/messages/mod',self.host,utils.messageQueryBody(subject,action,start,end,measure),self.auth.token)

    def getMessageVariance(self,subject,action,start=None,end=None,measure=None):
        """
        This function returns the variance from the messages present in the database for a certain Action, Subject and period

        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            start:  the lower end of the time period to be evaluated (optional)
            end:    the upper end of the time period to be evaluated (optional)
            measure:      The unit of measurement which the value should be displayed (optional)
        Returns:
            A Decimal
        Example:
            >>> print(getMessageVariance("CristianoRonaldo","DistanceCovered"))\n
            >>> 15.24
        """
        return httpHandler.get(self.url,'/api/messages/variance',self.host,utils.messageQueryBody(subject,action,start,end,measure),self.auth.token)
    
    def getMessageStdDev(self,subject,action,start=None,end=None,measure=None):
        """
        This function returns the standard deviation from the messages present in the database for a certain Action, Subject and period

        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            start:  the lower end of the time period to be evaluated (optional)
            end:    the upper end of the time period to be evaluated (optional)
            measure:      The unit of measurement which the value should be displayed (optional)
        Returns:
            A Decimal
        Example:
            >>> print(getMessageStdDev("CristianoRonaldo","DistanceCovered"))\n
            >>> 232.36
        """
        return httpHandler.get(self.url,'/api/messages/stddev',self.host,utils.messageQueryBody(subject,action,start,end,measure),self.auth.token)

    def getMessageKurtosis(self,subject,action,start=None,end=None):
        """
        This function returns the kurtosis from the messages present in the database for a certain Action, Subject and period

        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            start:  the lower end of the time period to be evaluated (optional)
            end:    the upper end of the time period to be evaluated (optional)
        Returns:
            A Decimal
        Example:
            >>> print(getMessageKurtosis("CristianoRonaldo","DistanceCovered"))\n
            >>> -0.177515
        """
        return httpHandler.get(self.url,'/api/messages/kurtosis',self.host,utils.messageQueryBody(subject,action,start,end),self.auth.token)

    def getMessageSkewness(self,subject,action,start=None,end=None):
        """
        This function returns the skewness from the messages present in the database for a certain Action, Subject and period

        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            start:  the lower end of the time period to be evaluated (optional)
            end:    the upper end of the time period to be evaluated (optional)
        Returns:
            A Decimal
        Example:
            >>> print(getMessageSkewness("CristianoRonaldo","DistanceCovered"))\n
            >>> -0.404796.
        """
        return httpHandler.get(self.url,'/api/messages/skewness',self.host,utils.messageQueryBody(subject,action,start,end),self.auth.token)

    def getMessageCountGroup(self,subject,action,aggregator,start=None,end=None,measure=None):
        """
        This function returns the amount of messages present in the database for a certain Action, Subject and period spread according the given aggregator

        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            aggregator:    the way we intend to spread the queried data
            start:  the lower end of the time period to be evaluated (optional)
            end:    the upper end of the time period to be evaluated (optional)
            measure:      The unit of measurement which the value should be displayed (optional)
        Returns:
            A String representation of an array of JSON objects indicating the aggregator component and it's value
        Example:
            >>> print(getMessageSumGroup("CristianoRonaldo","DistanceCovered",1))\n
            >>> "[{"day":"9","count":1}]"
        """
        return httpHandler.get(self.url,'/api/messages/countgroupby',self.host,utils.messageQueryGroupBody(subject,action,aggregator,start,end,measure),self.auth.token)

    def getMessageSumGroup(self,subject,action,aggregator,start=None,end=None,measure=None):
        """
        This function returns the sum of the values from the messages present in the database for a certain Action, Subject and period spread according the given aggregator

        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            aggregator:    the way we intend to spread the queried data
            start:  the lower end of the time period to be evaluated (optional)
            end:    the upper end of the time period to be evaluated (optional)
            measure:      The unit of measurement which the value should be displayed (optional)
        Returns:
            A String representation of an array of JSON objects indicating the aggregator component and it's value
        Example:
            >>> print(getMessageSumGroup("CristianoRonaldo","DistanceCovered",1))\n
            >>> "[{"day":"9","sum":11587.27}]"
        """
        return httpHandler.get(self.url,'/api/messages/sumgroupby',self.host,utils.messageQueryGroupBody(subject,action,aggregator,start,end,measure),self.auth.token)

    def getMessageAverageGroup(self,subject,action,aggregator,start=None,end=None,measure=None):
        """
        This function returns the average of the values from the messages present in the database for a certain Action, Subject and period spread according the given aggregator

        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            aggregator:    the way we intend to spread the queried data
            start:  the lower end of the time period to be evaluated (optional)
            end:    the upper end of the time period to be evaluated (optional)
            measure:      The unit of measurement which the value should be displayed (optional)
        Returns:
            A String representation of an array of JSON objects indicating the aggregator component and it's value
        Example:
            >>> print(getMessageAverageGroup("CristianoRonaldo","DistanceCovered",1))\n
            >>> "[{"day":"9","avg":11587.27}]"
        """
        return httpHandler.get(self.url,'/api/messages/avggroupby',self.host,utils.messageQueryGroupBody(subject,action,aggregator,start,end,measure),self.auth.token)

    def messageQuery(self,subject,action,start=None,end=None,measure=None):
        """
        This function returns all the messages present in the database for a certain Action, Subject and period 

        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            start:  the lower end of the time period to be evaluated (optional)
            end:    the upper end of the time period to be evaluated (optional)
            measure:      The unit of measurement which the value should be displayed (optional)
        Returns:
            A String representation of an array of JSON objects indicating the Message's date, it's creation date and the value of the message
        Example:
            >>> print(messageQuery("CristianoRonaldo","DistanceCovered"))\n
            >>> ">>> [{"date": "2021-07-09T16:47:36Z","value": 11587.27,"created": "2021-07-09T16:47:36Z"}]"
        """
        return httpHandler.get(self.url,'/api/messages',self.host,utils.messageQueryBody(subject,action,start,end,measure),self.auth.token)

    def messageOverview(self):
        """
        This function returns the amount of different actions and messages present in the database

        Returns:
            A String representation of a JSON object indicating the amount of messages and actions
        Example:
            >>> print(messageOverview())\n
            >>> "{"messages":1,"actions":1}"
        """
        return httpHandler.get(self.url,'/api/messages/overview',self.host,"",self.auth.token)

    def messageTopActionOverview(self):
        """
        This function returns an overview of the action with the most messages

        Returns:
            A String representation of a JSON object indicating the Action name, subject, value of the first message, date and the amount of messages
        Example:
            >>> print(messageTopActionOverview())\n
            >>> "{"name":"DistanceCovered","subject":"CristianoRonaldo","valueFirstMessage":11587.27,"unit":"Meter","date":"2021-07-09T16:47:36Z","total":1}"
        """
        return httpHandler.get(self.url,'/api/messages/topactionoverview',self.host,"",self.auth.token)
    
    #Role related requests

    def roleCreate(self,role):
        """
        This function inserts a Role into the database

        Args:
            role:    A role object
        Returns:
            An empty String in case of success
        Example:
            >>> role = Role("Position")\n
            >>> # properties = [[propertyName,propertyType],[...,...],...]\n
            >>> properties = [["PostionInText","text"]]\n
            >>> role.addProperties(properties)\n
            >>> roleCreate(role)
        """
        return httpHandler.post(self.url,'/api/role/create',self.host,utils.roleBody(role.key,role.properties),self.auth.token)

    def roleExists(self,role):
        """
        This function returns an existing Role in the database with a given identifier

        Args:
            role:    Role's unique identifier
        Returns:
            A String that represents a JSON object
        Example:
            >>> print(roleExists("Position"))\n
            >>> {"role": "Position","created": "2021-07-09T16:47:36Z","properties": [{"name": "PositionInText","type": "Text"}]}
        """
        return httpHandler.get(self.url,'/api/role/exist',self.host,utils.roleQueryBody(role),self.auth.token)

    def roleAll(self):
        """
        This function returns all the existing Roles in the database

        Returns:
            A String that represents an array of JSON object
        Example:
            >>> print(roleAll())\n
            >>> [{"role": "Position","created": "2021-07-09T16:47:36Z"}]
        """
        return httpHandler.get(self.url,'/api/role',self.host,"",self.auth.token)

    def roleAddActor(self,actorRole):
        """
        This function returns all the existing Roles in the database

        Args:
            actorRole: an ActorRole object that contains the actor key and role key to be associated and also the pretended properties
        Returns:
            An empty String in case of success
        Example:
            >>> actorRole = ActorRole("Postion","CristianoRonaldo")\n
            >>> # properties = [[propertyName,propertyValue],[...,...],...]\n
            >>> properties = [["PositionInText","Striker"]]\n
            >>> actorRole.addProperties(properties)\n
            >>> roleAddActor(actorRole)
        """
        return httpHandler.post(self.url,'/api/role/add',self.host,utils.roleAddActorBody(actorRole.roleKey,actorRole.actorKey,actorRole.properties),self.auth.token)

    def actorsByRole(self,role):
        """
        This function returns all the existing Actors in the database associated with a given role

        Args:
            role:    Role's unique identifier
        Returns:
            A String that represents an array of JSON objects
        Example:
            >>> print(actorsByRole("Position"))\n
            >>> [{"key": "Cristianoronaldo","Position": "Striker"}]
        """
        return httpHandler.get(self.url,'/api/role/actors',self.host,utils.roleQueryBody(role),self.auth.token)

    def roleProperties(self,role):
        """
        This function returns an existing Role and it's properties in the database with a given identifier

        Returns:
            A String that represents a JSON object
        Example:
            >>> print(roleProperties("Position"))\n
            >>> {"role": "Position","created": "2021-07-09T16:47:36Z","properties": [{"name": "PositionInText","type": "Text"}]}
        """
        return httpHandler.get(self.url,'/api/role/roleproperties',self.host,utils.roleQueryBody(role),self.auth.token)

    def topRoles(self):
        """
        This function returns the top 5 roles with the most messages sent

        Returns:
            A String that represents an array of JSON object
        Example:
            >>> print(topRoles())\n
            >>> [{"role":"Position","value":2}]
        """
        return httpHandler.get(self.url,'/api/role/toproles',self.host,"",self.auth.token)

    def roleTotalDataPoints(self,role):
        """
        This function returns the amount of Messages associated to a given Role

        Args:
            role:    Role's unique identifier
        Returns:
            An Integer
        Example:
            >>> Print(roleTotalDataPoints("Position"))\n
            >>> 2
        """
        return httpHandler.get(self.url,'/api/role/totaldatapoints',self.host,utils.roleQueryBody(role),self.auth.token)

#Alarms

    def AboveMovingAverageCreate(self,subject,action,measure,limit,snooze,callback,ttl):
        """
        This function creates an Above Moving Average alarm
        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            measure:      The unit of measurement which the alarm should monitor
            limit:      The threshold
            snooze:      The cooldown in minutes until the alarm should be able to trigger again
            callback:      The destination URL
            ttl:      The timeframe in minutes to be monitored (now - ttl)
        """
        return httpHandler.post(self.url,"/api/alarms/abovemovingaverage",self.host,utils.alarmsTtlCreateBody(subject,action,measure,limit,snooze,callback,ttl),self.auth.token)
        
    def AboveMovingAverageEdit(self,subject,action,measure,limit,snooze,callback,ttl):
        """
        This function edits an Above Moving Average alarm
        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            measure:      The unit of measurement which the alarm should monitor
            limit:      The threshold
            snooze:      The cooldown in minutes until the alarm should be able to trigger again
            callback:      The destination URL
            ttl:      The timeframe in minutes to be monitored (now - ttl)
        """
        return httpHandler.post(self.url,"/api/alarms/abovemovingaverage/edit",self.host,utils.alarmsTtlCreateBody(subject,action,measure,limit,snooze,callback,ttl),self.auth.token)
        
    def AboveMovingAverageDelete(self,subject,action):
        """
        This function deletes an Above Moving Average alarm
        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
        """
        return httpHandler.post(self.url,"/api/alarms/abovemovingaverage/delete",self.host,{"subject":subject,"action":action},self.auth.token)
        
    def AboveMovingAverageAll(self):
        """
        This function lists every active Above Moving Average Alarm
        """
        return httpHandler.get(self.url,"/api/alarms/abovemovingaverage/all",self.host,"",self.auth.token)
        
    def AboveThresholdCreate(self,subject,action,measure,limit,snooze,callback):
        """
        This function creates an Above Threshold alarm
        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            measure:      The unit of measurement which the alarm should monitor
            limit:      The threshold
            snooze:      The cooldown in minutes until the alarm should be able to trigger again
            callback:      The destination URL
        """
        return httpHandler.post(self.url,"/api/alarms/abovethreshold",self.host,utils.alarmsCreateBody(subject,action,measure,limit,snooze,callback),self.auth.token)
        
    def AboveThresholdEdit(self,subject,action,measure,limit,snooze,callback):
        """
        This function edits an Above Threshold alarm
        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            measure:      The unit of measurement which the alarm should monitor
            limit:      The threshold
            snooze:      The cooldown in minutes until the alarm should be able to trigger again
            callback:      The destination URL
        """
        return httpHandler.post(self.url,"/api/alarms/abovethreshold/edit",self.host,utils.alarmsCreateBody(subject,action,measure,limit,snooze,callback),self.auth.token)
        
    def AboveThresholdDelete(self,subject,action):
        """
        This function deletes an Above Threshold alarm
        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
        """
        return httpHandler.post(self.url,"/api/alarms/abovethreshold/delete",self.host,{"subject":subject,"action":action},self.auth.token)
        
    def AboveThresholdAll(self):
        """
        This function list every active Above Threshold Alarm
        """
        return httpHandler.get(self.url,"/api/alarms/abovethreshold/all",self.host,"",self.auth.token)
        
    def BelowMovingAverageCreate(self,subject,action,measure,limit,snooze,callback,ttl):
        """
        This function creates a Below Moving Average alarm
        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            measure:      The unit of measurement which the alarm should monitor
            limit:      The threshold
            snooze:      The cooldown in minutes until the alarm should be able to trigger again
            callback:      The destination URL
            ttl:      The timeframe in minutes to be monitored (now - ttl)
        """
        return httpHandler.post(self.url,"/api/alarms/belowmovingaverage",self.host,utils.alarmsTtlCreateBody(subject,action,measure,limit,snooze,callback,ttl),self.auth.token)

    def BelowMovingAverageEdit(self,subject,action,measure,limit,snooze,callback,ttl):
        """
        This function edits a Below Moving Average alarm
        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            measure:      The unit of measurement which the alarm should monitor
            limit:      The threshold
            snooze:      The cooldown in minutes until the alarm should be able to trigger again
            callback:      The destination URL
            ttl:      The timeframe in minutes to be monitored (now - ttl)
        """
        return httpHandler.post(self.url,"/api/alarms/belowmovingaverage/edit",self.host,utils.alarmsTtlCreateBody(subject,action,measure,limit,snooze,callback,ttl),self.auth.token)       

    def BelowMovingAverageDelete(self,subject,action):
        """
        This function deletes a Below Moving Average alarm
        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
        """
        return httpHandler.post(self.url,"/api/alarms/belowmovingaverage/delete",self.host,{"subject":subject,"action":action},self.auth.token)

    def BelowMovingAverageAll(self):
        """
        This function lists every active Below Moving Average Alarm
        """
        return httpHandler.get(self.url,"/api/alarms/belowmovingaverage/all",self.host,"",self.auth.token)

    def BelowThresholdCreate(self,subject,action,measure,limit,snooze,callback):
        """
        This function creates a Below Threshold alarm
        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            measure:      The unit of measurement which the alarm should monitor
            limit:      The threshold
            snooze:      The cooldown in minutes until the alarm should be able to trigger again
            callback:      The destination URL
        """
        return httpHandler.post(self.url,"/api/alarms/belowthreshold",self.host,utils.alarmsCreateBody(subject,action,measure,limit,snooze,callback),self.auth.token)

    def BelowThresholdEdit(self,subject,action,measure,limit,snooze,callback):
        """
        This function edits a Below Threshold alarm
        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            measure:      The unit of measurement which the alarm should monitor
            limit:      The threshold
            snooze:      The cooldown in minutes until the alarm should be able to trigger again
            callback:      The destination URL
        """
        return httpHandler.post(self.url,"/api/alarms/belowthreshold/edit",self.host,utils.alarmsCreateBody(subject,action,measure,limit,snooze,callback),self.auth.token)

    def BelowThresholdDelete(self,subject,action):
        """
        This function deletes a Below Threshold alarm
        Args:
            subject:    Actor's unique identifier
            action:    Action's identifie
        """
        return httpHandler.post(self.url,"/api/alarms/belowthreshold/delete",self.host,{"subject":subject,"action":action},self.auth.token)

    def BelowThresholdAll(self):
        """
        This function lists every active Below Threshold Alarm
        """
        return httpHandler.get(self.url,"/api/alarms/belowthreshold/all",self.host,"",self.auth.token)

    def SignalVariabiltiyCreate(self,subject,action,measure,limit,snooze,callback,ttl):
        """
        This function creates a Signal Variability alarm
        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            measure:      The unit of measurement which the alarm should monitor
            limit:      The threshold
            snooze:      The cooldown in minutes until the alarm should be able to trigger again
            callback:      The destination URL
            ttl:      The timeframe in minutes to be monitored (now - ttl)
        """
        return httpHandler.post(self.url,"/api/alarms/signalvariability",self.host,utils.alarmsTtlCreateBody(subject,action,measure,limit,snooze,callback,ttl),self.auth.token)        

    def SignalVariabiltiyEdit(self,subject,action,measure,limit,snooze,callback,ttl):
        """
        This function edits a Signal Variability alarm
        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
            measure:      The unit of measurement which the alarm should monitor
            limit:      The threshold
            snooze:      The cooldown in minutes until the alarm should be able to trigger again
            callback:      The destination URL
            ttl:      The timeframe in minutes to be monitored (now - ttl)
        """
        return httpHandler.post(self.url,"/api/alarms/signalvariability/edit",self.host,utils.alarmsTtlCreateBody(subject,action,measure,limit,snooze,callback,ttl),self.auth.token)        

    def SignalVariabiltiyDelete(self,subject,action):
        """
        This function deletes a Signal Variability alarm
        Args:
            subject:    Actor's unique identifier
            action:    Action's identifier
        """
        return httpHandler.post(self.url,"/api/alarms/signalvariability/delete",self.host,{"subject":subject,"action":action},self.auth.token)

    def SignalVariabiltiyAll(self):
        """
        This function lists every active Signal Variability Alarm
        """
        return httpHandler.get(self.url,"/api/alarms/signalvariability/all",self.host,"",self.auth.token)

#Available Measures

def AbsorbedDoseGray():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AbsorbedDoseGray())
        >>> {"dimension":0,"unit":30120}
    """
    return {"dimension" : 0, "unit" : 30120}

def AbsorbedDoseKilogray():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AbsorbedDoseKilogray())
        >>> {"dimension":0,"unit":959}
    """
    return {"dimension" : 0, "unit" : 959}

def AbsorbedDoseMegagray():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AbsorbedDoseMegagray())
        >>> {"dimension":0,"unit":18479}
    """
    return {"dimension" : 0, "unit" : 18479}

def AbsorbedDoseGigagray():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AbsorbedDoseGigagray())
        >>> {"dimension":0,"unit":4776}
    """
    return {"dimension" : 0, "unit" : 4776}

def AbsorbedDoseMilligray():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AbsorbedDoseMilligray())
        >>> {"dimension":0,"unit":5647}
    """
    return {"dimension" : 0, "unit" : 5647}

def AbsorbedDoseMicrogray():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AbsorbedDoseMicrogray())
        >>> {"dimension":0,"unit":11598}
    """
    return {"dimension" : 0, "unit" : 11598}

def AbsorbedDoseNanogray():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AbsorbedDoseNanogray())
        >>> {"dimension":0,"unit":12501}
    """
    return {"dimension" : 0, "unit" : 12501}

def AccelerationMeterPerSecondSquared():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AccelerationMeterPerSecondSquared())
        >>> {"dimension":1,"unit":25020}
    """
    return {"dimension" : 1, "unit" : 25020}

def AccelerationKilometerPerSecondSquared():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AccelerationKilometerPerSecondSquared())
        >>> {"dimension":1,"unit":6161}
    """
    return {"dimension" : 1, "unit" : 6161}

def AccelerationCentimeterPerSecondSquared():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AccelerationCentimeterPerSecondSquared())
        >>> {"dimension":1,"unit":28649}
    """
    return {"dimension" : 1, "unit" : 28649}

def AccelerationMillimeterPerSecondSquared():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AccelerationMillimeterPerSecondSquared())
        >>> {"dimension":1,"unit":26607}
    """
    return {"dimension" : 1, "unit" : 26607}

def ActionJoulePerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ActionJoulePerSecond())
        >>> {"dimension":2,"unit":20914}
    """
    return {"dimension" : 2, "unit" : 20914}

def ActionKilojoulePerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ActionKilojoulePerSecond())
        >>> {"dimension":2,"unit":19276}
    """
    return {"dimension" : 2, "unit" : 19276}

def ActionMegajoulePerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ActionMegajoulePerSecond())
        >>> {"dimension":2,"unit":21871}
    """
    return {"dimension" : 2, "unit" : 21871}

def ActionGigajoulePerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ActionGigajoulePerSecond())
        >>> {"dimension":2,"unit":19754}
    """
    return {"dimension" : 2, "unit" : 19754}

def ActionMillijoulePerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ActionMillijoulePerSecond())
        >>> {"dimension":2,"unit":14732}
    """
    return {"dimension" : 2, "unit" : 14732}

def ActionMicrojoulePerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ActionMicrojoulePerSecond())
        >>> {"dimension":2,"unit":22003}
    """
    return {"dimension" : 2, "unit" : 22003}

def ActionNanojoulePerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ActionNanojoulePerSecond())
        >>> {"dimension":2,"unit":23621}
    """
    return {"dimension" : 2, "unit" : 23621}

def ActionCaloriesPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ActionCaloriesPerSecond())
        >>> {"dimension":2,"unit":31167}
    """
    return {"dimension" : 2, "unit" : 31167}

def ActionKilocaloriesPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ActionKilocaloriesPerSecond())
        >>> {"dimension":2,"unit":31745}
    """
    return {"dimension" : 2, "unit" : 31745}

def ActivityBecquerel():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ActivityBecquerel())
        >>> {"dimension":3,"unit":26694}
    """
    return {"dimension" : 3, "unit" : 26694}

def ActivityKilobecquerel():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ActivityKilobecquerel())
        >>> {"dimension":3,"unit":23401}
    """
    return {"dimension" : 3, "unit" : 23401}

def ActivityMegabecquerel():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ActivityMegabecquerel())
        >>> {"dimension":3,"unit":3567}
    """
    return {"dimension" : 3, "unit" : 3567}

def ActivityGigabecquerel():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ActivityGigabecquerel())
        >>> {"dimension":3,"unit":6547}
    """
    return {"dimension" : 3, "unit" : 6547}

def ActivityMillibecquerel():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ActivityMillibecquerel())
        >>> {"dimension":3,"unit":4912}
    """
    return {"dimension" : 3, "unit" : 4912}

def ActivityMicrobecquerel():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ActivityMicrobecquerel())
        >>> {"dimension":3,"unit":28879}
    """
    return {"dimension" : 3, "unit" : 28879}

def ActivityNanobecquerel():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ActivityNanobecquerel())
        >>> {"dimension":3,"unit":23007}
    """
    return {"dimension" : 3, "unit" : 23007}

def AmountMole():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AmountMole())
        >>> {"dimension":4,"unit":13449}
    """
    return {"dimension" : 4, "unit" : 13449}

def AmountKilomole():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AmountKilomole())
        >>> {"dimension":4,"unit":17055}
    """
    return {"dimension" : 4, "unit" : 17055}

def AmountMegamole():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AmountMegamole())
        >>> {"dimension":4,"unit":1808}
    """
    return {"dimension" : 4, "unit" : 1808}

def AmountGigamole():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AmountGigamole())
        >>> {"dimension":4,"unit":20872}
    """
    return {"dimension" : 4, "unit" : 20872}

def AmountMillimole():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AmountMillimole())
        >>> {"dimension":4,"unit":21743}
    """
    return {"dimension" : 4, "unit" : 21743}

def AmountMicromole():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AmountMicromole())
        >>> {"dimension":4,"unit":27694}
    """
    return {"dimension" : 4, "unit" : 27694}

def AmountNanomole():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AmountNanomole())
        >>> {"dimension":4,"unit":28597}
    """
    return {"dimension" : 4, "unit" : 28597}

def AngularAccelerationRadianSquareSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AngularAccelerationRadianSquareSecond())
        >>> {"dimension":5,"unit":11247}
    """
    return {"dimension" : 5, "unit" : 11247}

def AngularAccelerationRadianSquareMinute():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AngularAccelerationRadianSquareMinute())
        >>> {"dimension":5,"unit":8520}
    """
    return {"dimension" : 5, "unit" : 8520}

def AngularAccelerationRevolutionSquareSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AngularAccelerationRevolutionSquareSecond())
        >>> {"dimension":5,"unit":28224}
    """
    return {"dimension" : 5, "unit" : 28224}

def AngularAccelerationRevolutionSquareMinute():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AngularAccelerationRevolutionSquareMinute())
        >>> {"dimension":5,"unit":25493}
    """
    return {"dimension" : 5, "unit" : 25493}

def AngularAccelerationRevolutionsPerMinutePerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AngularAccelerationRevolutionsPerMinutePerSecond())
        >>> {"dimension":5,"unit":24453}
    """
    return {"dimension" : 5, "unit" : 24453}

def AngularMomentumKilogramMetersSquaredPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AngularMomentumKilogramMetersSquaredPerSecond())
        >>> {"dimension":6,"unit":7384}
    """
    return {"dimension" : 6, "unit" : 7384}

def AngularMomentumGramMetersSquaredPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AngularMomentumGramMetersSquaredPerSecond())
        >>> {"dimension":6,"unit":21632}
    """
    return {"dimension" : 6, "unit" : 21632}

def AngularVelocityRadianPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AngularVelocityRadianPerSecond())
        >>> {"dimension":7,"unit":24796}
    """
    return {"dimension" : 7, "unit" : 24796}

def AngularVelocityRadianPerMinute():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AngularVelocityRadianPerMinute())
        >>> {"dimension":7,"unit":22065}
    """
    return {"dimension" : 7, "unit" : 22065}

def AngularVelocityRevolutionPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AngularVelocityRevolutionPerSecond())
        >>> {"dimension":7,"unit":13040}
    """
    return {"dimension" : 7, "unit" : 13040}

def AngularVelocityRevolutionPerMinute():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AngularVelocityRevolutionPerMinute())
        >>> {"dimension":7,"unit":10309}
    """
    return {"dimension" : 7, "unit" : 10309}

def AreaSquareMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AreaSquareMeter())
        >>> {"dimension":8,"unit":21843}
    """
    return {"dimension" : 8, "unit" : 21843}

def AreaSquareCentimeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AreaSquareCentimeter())
        >>> {"dimension":8,"unit":1259}
    """
    return {"dimension" : 8, "unit" : 1259}

def AreaSquareMillimeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AreaSquareMillimeter())
        >>> {"dimension":8,"unit":22649}
    """
    return {"dimension" : 8, "unit" : 22649}

def AreaSquareKilometer():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AreaSquareKilometer())
        >>> {"dimension":8,"unit":24991}
    """
    return {"dimension" : 8, "unit" : 24991}

def AreaHectare():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(AreaHectare())
        >>> {"dimension":8,"unit":3430}
    """
    return {"dimension" : 8, "unit" : 3430}

def CapacitanceFarad():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CapacitanceFarad())
        >>> {"dimension":9,"unit":1275}
    """
    return {"dimension" : 9, "unit" : 1275}

def CapacitanceKilofarad():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CapacitanceKilofarad())
        >>> {"dimension":9,"unit":21928}
    """
    return {"dimension" : 9, "unit" : 21928}

def CapacitanceMegafarad():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CapacitanceMegafarad())
        >>> {"dimension":9,"unit":10338}
    """
    return {"dimension" : 9, "unit" : 10338}

def CapacitanceGigafarad():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CapacitanceGigafarad())
        >>> {"dimension":9,"unit":16921}
    """
    return {"dimension" : 9, "unit" : 16921}

def CapacitanceMillifarad():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CapacitanceMillifarad())
        >>> {"dimension":9,"unit":12785}
    """
    return {"dimension" : 9, "unit" : 12785}

def CapacitanceMicrofarad():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CapacitanceMicrofarad())
        >>> {"dimension":9,"unit":12650}
    """
    return {"dimension" : 9, "unit" : 12650}

def CapacitanceNanofarad():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CapacitanceNanofarad())
        >>> {"dimension":9,"unit":9694}
    """
    return {"dimension" : 9, "unit" : 9694}

def CatalyticActivityKatal():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CatalyticActivityKatal())
        >>> {"dimension":10,"unit":2239}
    """
    return {"dimension" : 10, "unit" : 2239}

def CatalyticActivityKilokatal():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CatalyticActivityKilokatal())
        >>> {"dimension":10,"unit":22892}
    """
    return {"dimension" : 10, "unit" : 22892}

def CatalyticActivityMegakatal():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CatalyticActivityMegakatal())
        >>> {"dimension":10,"unit":11302}
    """
    return {"dimension" : 10, "unit" : 11302}

def CatalyticActivityGigakatal():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CatalyticActivityGigakatal())
        >>> {"dimension":10,"unit":17885}
    """
    return {"dimension" : 10, "unit" : 17885}

def CatalyticActivityMillikatal():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CatalyticActivityMillikatal())
        >>> {"dimension":10,"unit":13749}
    """
    return {"dimension" : 10, "unit" : 13749}

def CatalyticActivityMicrokatal():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CatalyticActivityMicrokatal())
        >>> {"dimension":10,"unit":13614}
    """
    return {"dimension" : 10, "unit" : 13614}

def CatalyticActivityNanokatal():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CatalyticActivityNanokatal())
        >>> {"dimension":10,"unit":10658}
    """
    return {"dimension" : 10, "unit" : 10658}

def ConductanceSiemens():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ConductanceSiemens())
        >>> {"dimension":11,"unit":26506}
    """
    return {"dimension" : 11, "unit" : 26506}

def ConductanceKilosiemens():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ConductanceKilosiemens())
        >>> {"dimension":11,"unit":6734}
    """
    return {"dimension" : 11, "unit" : 6734}

def ConductanceMegasiemens():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ConductanceMegasiemens())
        >>> {"dimension":11,"unit":30726}
    """
    return {"dimension" : 11, "unit" : 30726}

def ConductanceGigasiemens():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ConductanceGigasiemens())
        >>> {"dimension":11,"unit":23808}
    """
    return {"dimension" : 11, "unit" : 23808}

def ConductanceMillisiemens():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ConductanceMillisiemens())
        >>> {"dimension":11,"unit":7739}
    """
    return {"dimension" : 11, "unit" : 7739}

def ConductanceMicrosiemens():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ConductanceMicrosiemens())
        >>> {"dimension":11,"unit":26507}
    """
    return {"dimension" : 11, "unit" : 26507}

def ConductanceNanosiemens():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ConductanceNanosiemens())
        >>> {"dimension":11,"unit":17537}
    """
    return {"dimension" : 11, "unit" : 17537}

def ConductivitySiemensPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ConductivitySiemensPerMeter())
        >>> {"dimension":12,"unit":11009}
    """
    return {"dimension" : 12, "unit" : 11009}

def ConductivityKilosiemensPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ConductivityKilosiemensPerMeter())
        >>> {"dimension":12,"unit":22505}
    """
    return {"dimension" : 12, "unit" : 22505}

def ConductivityMegasiemensPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ConductivityMegasiemensPerMeter())
        >>> {"dimension":12,"unit":9819}
    """
    return {"dimension" : 12, "unit" : 9819}

def ConductivityGigasiemensPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ConductivityGigasiemensPerMeter())
        >>> {"dimension":12,"unit":5496}
    """
    return {"dimension" : 12, "unit" : 5496}

def ConductivityMillisiemensPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ConductivityMillisiemensPerMeter())
        >>> {"dimension":12,"unit":3585}
    """
    return {"dimension" : 12, "unit" : 3585}

def ConductivityMicrosiemensPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ConductivityMicrosiemensPerMeter())
        >>> {"dimension":12,"unit":14183}
    """
    return {"dimension" : 12, "unit" : 14183}

def ConductivityNanosiemensPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ConductivityNanosiemensPerMeter())
        >>> {"dimension":12,"unit":2091}
    """
    return {"dimension" : 12, "unit" : 2091}

def CurrencyMoney():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CurrencyMoney())
        >>> {"dimension":13,"unit":20081}
    """
    return {"dimension" : 13, "unit" : 20081}

def CurrentAmpere():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CurrentAmpere())
        >>> {"dimension":14,"unit":25616}
    """
    return {"dimension" : 14, "unit" : 25616}

def CurrentKiloampere():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CurrentKiloampere())
        >>> {"dimension":14,"unit":19058}
    """
    return {"dimension" : 14, "unit" : 19058}

def CurrentMegaampere():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CurrentMegaampere())
        >>> {"dimension":14,"unit":29712}
    """
    return {"dimension" : 14, "unit" : 29712}

def CurrentGigaampere():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CurrentGigaampere())
        >>> {"dimension":14,"unit":17590}
    """
    return {"dimension" : 14, "unit" : 17590}

def CurrentMilliampere():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CurrentMilliampere())
        >>> {"dimension":14,"unit":12138}
    """
    return {"dimension" : 14, "unit" : 12138}

def CurrentMicroampere():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CurrentMicroampere())
        >>> {"dimension":14,"unit":7743}
    """
    return {"dimension" : 14, "unit" : 7743}

def CurrentNanoampere():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CurrentNanoampere())
        >>> {"dimension":14,"unit":8464}
    """
    return {"dimension" : 14, "unit" : 8464}

def CustomCustom():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(CustomCustom())
        >>> {"dimension":15,"unit":26731}
    """
    return {"dimension" : 15, "unit" : 26731}

def DataTransferBitPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DataTransferBitPerSecond())
        >>> {"dimension":16,"unit":6613}
    """
    return {"dimension" : 16, "unit" : 6613}

def DataTransferKilobitPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DataTransferKilobitPerSecond())
        >>> {"dimension":16,"unit":684}
    """
    return {"dimension" : 16, "unit" : 684}

def DataTransferKilobytePerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DataTransferKilobytePerSecond())
        >>> {"dimension":16,"unit":20153}
    """
    return {"dimension" : 16, "unit" : 20153}

def DataTransferKibibitPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DataTransferKibibitPerSecond())
        >>> {"dimension":16,"unit":23002}
    """
    return {"dimension" : 16, "unit" : 23002}

def DataTransferMegabitPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DataTransferMegabitPerSecond())
        >>> {"dimension":16,"unit":19614}
    """
    return {"dimension" : 16, "unit" : 19614}

def DataTransferMegabytePerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DataTransferMegabytePerSecond())
        >>> {"dimension":16,"unit":22218}
    """
    return {"dimension" : 16, "unit" : 22218}

def DataTransferMebibitPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DataTransferMebibitPerSecond())
        >>> {"dimension":16,"unit":14244}
    """
    return {"dimension" : 16, "unit" : 14244}

def DataTransferGigabitPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DataTransferGigabitPerSecond())
        >>> {"dimension":16,"unit":30112}
    """
    return {"dimension" : 16, "unit" : 30112}

def DataTransferGigabytePerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DataTransferGigabytePerSecond())
        >>> {"dimension":16,"unit":8251}
    """
    return {"dimension" : 16, "unit" : 8251}

def DataTransferGibibitPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DataTransferGibibitPerSecond())
        >>> {"dimension":16,"unit":24742}
    """
    return {"dimension" : 16, "unit" : 24742}

def DataTransferTerabitPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DataTransferTerabitPerSecond())
        >>> {"dimension":16,"unit":28151}
    """
    return {"dimension" : 16, "unit" : 28151}

def DataTransferTerabytePerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DataTransferTerabytePerSecond())
        >>> {"dimension":16,"unit":9028}
    """
    return {"dimension" : 16, "unit" : 9028}

def DataTransferTebibitPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DataTransferTebibitPerSecond())
        >>> {"dimension":16,"unit":11199}
    """
    return {"dimension" : 16, "unit" : 11199}

def DoseEquivalentSievert():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DoseEquivalentSievert())
        >>> {"dimension":17,"unit":22402}
    """
    return {"dimension" : 17, "unit" : 22402}

def DoseEquivalentKilosievert():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DoseEquivalentKilosievert())
        >>> {"dimension":17,"unit":2630}
    """
    return {"dimension" : 17, "unit" : 2630}

def DoseEquivalentMegasievert():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DoseEquivalentMegasievert())
        >>> {"dimension":17,"unit":26622}
    """
    return {"dimension" : 17, "unit" : 26622}

def DoseEquivalentGigasievert():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DoseEquivalentGigasievert())
        >>> {"dimension":17,"unit":19704}
    """
    return {"dimension" : 17, "unit" : 19704}

def DoseEquivalentMillisievert():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DoseEquivalentMillisievert())
        >>> {"dimension":17,"unit":3635}
    """
    return {"dimension" : 17, "unit" : 3635}

def DoseEquivalentMicrosievert():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DoseEquivalentMicrosievert())
        >>> {"dimension":17,"unit":22403}
    """
    return {"dimension" : 17, "unit" : 22403}

def DoseEquivalentNanosievert():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DoseEquivalentNanosievert())
        >>> {"dimension":17,"unit":13433}
    """
    return {"dimension" : 17, "unit" : 13433}

def DynamicViscosityPascalSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DynamicViscosityPascalSecond())
        >>> {"dimension":18,"unit":28805}
    """
    return {"dimension" : 18, "unit" : 28805}

def DynamicViscosityKilopascalSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DynamicViscosityKilopascalSecond())
        >>> {"dimension":18,"unit":17703}
    """
    return {"dimension" : 18, "unit" : 17703}

def DynamicViscosityMegapascalSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DynamicViscosityMegapascalSecond())
        >>> {"dimension":18,"unit":13310}
    """
    return {"dimension" : 18, "unit" : 13310}

def DynamicViscosityGigapascalSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DynamicViscosityGigapascalSecond())
        >>> {"dimension":18,"unit":32497}
    """
    return {"dimension" : 18, "unit" : 32497}

def DynamicViscosityMillipascalSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DynamicViscosityMillipascalSecond())
        >>> {"dimension":18,"unit":23092}
    """
    return {"dimension" : 18, "unit" : 23092}

def DynamicViscosityMicropascalSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DynamicViscosityMicropascalSecond())
        >>> {"dimension":18,"unit":1078}
    """
    return {"dimension" : 18, "unit" : 1078}

def DynamicViscosityNanopascalSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DynamicViscosityNanopascalSecond())
        >>> {"dimension":18,"unit":21129}
    """
    return {"dimension" : 18, "unit" : 21129}

def ElectricChargeCoulomb():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ElectricChargeCoulomb())
        >>> {"dimension":19,"unit":13377}
    """
    return {"dimension" : 19, "unit" : 13377}

def ElectricChargeKilocoulomb():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ElectricChargeKilocoulomb())
        >>> {"dimension":19,"unit":26372}
    """
    return {"dimension" : 19, "unit" : 26372}

def ElectricChargeMegacoulomb():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ElectricChargeMegacoulomb())
        >>> {"dimension":19,"unit":17597}
    """
    return {"dimension" : 19, "unit" : 17597}

def ElectricChargeGigacoulomb():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ElectricChargeGigacoulomb())
        >>> {"dimension":19,"unit":10679}
    """
    return {"dimension" : 19, "unit" : 10679}

def ElectricChargeMillicoulomb():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ElectricChargeMillicoulomb())
        >>> {"dimension":19,"unit":27377}
    """
    return {"dimension" : 19, "unit" : 27377}

def ElectricChargeMicrocoulomb():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ElectricChargeMicrocoulomb())
        >>> {"dimension":19,"unit":13378}
    """
    return {"dimension" : 19, "unit" : 13378}

def ElectricChargeNanocoulomb():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ElectricChargeNanocoulomb())
        >>> {"dimension":19,"unit":4404}
    """
    return {"dimension" : 19, "unit" : 4404}

def ElectricPotentialVolt():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ElectricPotentialVolt())
        >>> {"dimension":20,"unit":9227}
    """
    return {"dimension" : 20, "unit" : 9227}

def ElectricPotentialKilovolt():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ElectricPotentialKilovolt())
        >>> {"dimension":20,"unit":12833}
    """
    return {"dimension" : 20, "unit" : 12833}

def ElectricPotentialMegavolt():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ElectricPotentialMegavolt())
        >>> {"dimension":20,"unit":30353}
    """
    return {"dimension" : 20, "unit" : 30353}

def ElectricPotentialGigavolt():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ElectricPotentialGigavolt())
        >>> {"dimension":20,"unit":16650}
    """
    return {"dimension" : 20, "unit" : 16650}

def ElectricPotentialMillivolt():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ElectricPotentialMillivolt())
        >>> {"dimension":20,"unit":17521}
    """
    return {"dimension" : 20, "unit" : 17521}

def ElectricPotentialMicrovolt():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ElectricPotentialMicrovolt())
        >>> {"dimension":20,"unit":23472}
    """
    return {"dimension" : 20, "unit" : 23472}

def ElectricPotentialNanovolt():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ElectricPotentialNanovolt())
        >>> {"dimension":20,"unit":24375}
    """
    return {"dimension" : 20, "unit" : 24375}

def EnergyJoule():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(EnergyJoule())
        >>> {"dimension":21,"unit":8988}
    """
    return {"dimension" : 21, "unit" : 8988}

def EnergyKilojoule():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(EnergyKilojoule())
        >>> {"dimension":21,"unit":29641}
    """
    return {"dimension" : 21, "unit" : 29641}

def EnergyMegajoule():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(EnergyMegajoule())
        >>> {"dimension":21,"unit":18051}
    """
    return {"dimension" : 21, "unit" : 18051}

def EnergyGigajoule():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(EnergyGigajoule())
        >>> {"dimension":21,"unit":24634}
    """
    return {"dimension" : 21, "unit" : 24634}

def EnergyMillijoule():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(EnergyMillijoule())
        >>> {"dimension":21,"unit":20498}
    """
    return {"dimension" : 21, "unit" : 20498}

def EnergyMicrojoule():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(EnergyMicrojoule())
        >>> {"dimension":21,"unit":20363}
    """
    return {"dimension" : 21, "unit" : 20363}

def EnergyNanojoule():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(EnergyNanojoule())
        >>> {"dimension":21,"unit":17407}
    """
    return {"dimension" : 21, "unit" : 17407}

def EnergyCalories():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(EnergyCalories())
        >>> {"dimension":21,"unit":17750}
    """
    return {"dimension" : 21, "unit" : 17750}

def EnergyKilocalories():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(EnergyKilocalories())
        >>> {"dimension":21,"unit":20630}
    """
    return {"dimension" : 21, "unit" : 20630}

def ForceNewton():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ForceNewton())
        >>> {"dimension":22,"unit":475}
    """
    return {"dimension" : 22, "unit" : 475}

def ForceKilonewton():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ForceKilonewton())
        >>> {"dimension":22,"unit":26688}
    """
    return {"dimension" : 22, "unit" : 26688}

def ForceMeganewton():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ForceMeganewton())
        >>> {"dimension":22,"unit":4575}
    """
    return {"dimension" : 22, "unit" : 4575}

def ForceGiganewton():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ForceGiganewton())
        >>> {"dimension":22,"unit":25220}
    """
    return {"dimension" : 22, "unit" : 25220}

def ForceMillinewton():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ForceMillinewton())
        >>> {"dimension":22,"unit":19768}
    """
    return {"dimension" : 22, "unit" : 19768}

def ForceMicronewton():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ForceMicronewton())
        >>> {"dimension":22,"unit":15369}
    """
    return {"dimension" : 22, "unit" : 15369}

def ForceNanonewton():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ForceNanonewton())
        >>> {"dimension":22,"unit":16090}
    """
    return {"dimension" : 22, "unit" : 16090}

def FrequencyHertz():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(FrequencyHertz())
        >>> {"dimension":23,"unit":27222}
    """
    return {"dimension" : 23, "unit" : 27222}

def FrequencyKilohertz():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(FrequencyKilohertz())
        >>> {"dimension":23,"unit":15108}
    """
    return {"dimension" : 23, "unit" : 15108}

def FrequencyMegahertz():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(FrequencyMegahertz())
        >>> {"dimension":23,"unit":3518}
    """
    return {"dimension" : 23, "unit" : 3518}

def FrequencyGigahertz():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(FrequencyGigahertz())
        >>> {"dimension":23,"unit":10101}
    """
    return {"dimension" : 23, "unit" : 10101}

def FrequencyMillihertz():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(FrequencyMillihertz())
        >>> {"dimension":23,"unit":5965}
    """
    return {"dimension" : 23, "unit" : 5965}

def FrequencyMicrohertz():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(FrequencyMicrohertz())
        >>> {"dimension":23,"unit":5830}
    """
    return {"dimension" : 23, "unit" : 5830}

def FrequencyNanohertz():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(FrequencyNanohertz())
        >>> {"dimension":23,"unit":2874}
    """
    return {"dimension" : 23, "unit" : 2874}

def IlluminanceLux():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(IlluminanceLux())
        >>> {"dimension":24,"unit":9455}
    """
    return {"dimension" : 24, "unit" : 9455}

def IlluminanceKilolux():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(IlluminanceKilolux())
        >>> {"dimension":24,"unit":5593}
    """
    return {"dimension" : 24, "unit" : 5593}

def IlluminanceMegalux():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(IlluminanceMegalux())
        >>> {"dimension":24,"unit":25985}
    """
    return {"dimension" : 24, "unit" : 25985}

def IlluminanceGigalux():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(IlluminanceGigalux())
        >>> {"dimension":24,"unit":4719}
    """
    return {"dimension" : 24, "unit" : 4719}

def IlluminanceMillilux():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(IlluminanceMillilux())
        >>> {"dimension":24,"unit":5737}
    """
    return {"dimension" : 24, "unit" : 5737}

def IlluminanceMicrolux():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(IlluminanceMicrolux())
        >>> {"dimension":24,"unit":23790}
    """
    return {"dimension" : 24, "unit" : 23790}

def IlluminanceNanolux():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(IlluminanceNanolux())
        >>> {"dimension":24,"unit":24808}
    """
    return {"dimension" : 24, "unit" : 24808}

def ImpedanceOhm():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ImpedanceOhm())
        >>> {"dimension":25,"unit":12282}
    """
    return {"dimension" : 25, "unit" : 12282}

def ImpedanceKiloohm():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ImpedanceKiloohm())
        >>> {"dimension":25,"unit":8420}
    """
    return {"dimension" : 25, "unit" : 8420}

def ImpedanceMegaohm():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ImpedanceMegaohm())
        >>> {"dimension":25,"unit":28812}
    """
    return {"dimension" : 25, "unit" : 28812}

def ImpedanceGigaohm():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ImpedanceGigaohm())
        >>> {"dimension":25,"unit":7546}
    """
    return {"dimension" : 25, "unit" : 7546}

def ImpedanceMilliohm():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ImpedanceMilliohm())
        >>> {"dimension":25,"unit":8564}
    """
    return {"dimension" : 25, "unit" : 8564}

def ImpedanceMicroohm():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ImpedanceMicroohm())
        >>> {"dimension":25,"unit":26617}
    """
    return {"dimension" : 25, "unit" : 26617}

def ImpedanceNanoohm():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ImpedanceNanoohm())
        >>> {"dimension":25,"unit":27635}
    """
    return {"dimension" : 25, "unit" : 27635}

def InformationBit():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(InformationBit())
        >>> {"dimension":26,"unit":30932}
    """
    return {"dimension" : 26, "unit" : 30932}

def InformationByte():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(InformationByte())
        >>> {"dimension":26,"unit":22500}
    """
    return {"dimension" : 26, "unit" : 22500}

def KinematicViscositySquareMetersPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(KinematicViscositySquareMetersPerSecond())
        >>> {"dimension":27,"unit":23788}
    """
    return {"dimension" : 27, "unit" : 23788}

def KinematicViscositySquareCentimetersPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(KinematicViscositySquareCentimetersPerSecond())
        >>> {"dimension":27,"unit":14072}
    """
    return {"dimension" : 27, "unit" : 14072}

def KinematicViscositySquareMillimetersPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(KinematicViscositySquareMillimetersPerSecond())
        >>> {"dimension":27,"unit":15381}
    """
    return {"dimension" : 27, "unit" : 15381}

def KinematicViscositySquareKilometersPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(KinematicViscositySquareKilometersPerSecond())
        >>> {"dimension":27,"unit":32185}
    """
    return {"dimension" : 27, "unit" : 32185}

def LengthMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LengthMeter())
        >>> {"dimension":28,"unit":27675}
    """
    return {"dimension" : 28, "unit" : 27675}

def LengthKilometer():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LengthKilometer())
        >>> {"dimension":28,"unit":15561}
    """
    return {"dimension" : 28, "unit" : 15561}

def LengthCentimeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LengthCentimeter())
        >>> {"dimension":28,"unit":17791}
    """
    return {"dimension" : 28, "unit" : 17791}

def LengthMillimeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LengthMillimeter())
        >>> {"dimension":28,"unit":6418}
    """
    return {"dimension" : 28, "unit" : 6418}

def LengthMicrometer():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LengthMicrometer())
        >>> {"dimension":28,"unit":6283}
    """
    return {"dimension" : 28, "unit" : 6283}

def LengthNanometer():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LengthNanometer())
        >>> {"dimension":28,"unit":3327}
    """
    return {"dimension" : 28, "unit" : 3327}

def LuminousFluxLumen():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LuminousFluxLumen())
        >>> {"dimension":29,"unit":31692}
    """
    return {"dimension" : 29, "unit" : 31692}

def LuminousFluxKilolumen():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LuminousFluxKilolumen())
        >>> {"dimension":29,"unit":19578}
    """
    return {"dimension" : 29, "unit" : 19578}

def LuminousFluxMegalumen():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LuminousFluxMegalumen())
        >>> {"dimension":29,"unit":7988}
    """
    return {"dimension" : 29, "unit" : 7988}

def LuminousFluxGigalumen():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LuminousFluxGigalumen())
        >>> {"dimension":29,"unit":14571}
    """
    return {"dimension" : 29, "unit" : 14571}

def LuminousFluxMillilumen():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LuminousFluxMillilumen())
        >>> {"dimension":29,"unit":10435}
    """
    return {"dimension" : 29, "unit" : 10435}

def LuminousFluxMicrolumen():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LuminousFluxMicrolumen())
        >>> {"dimension":29,"unit":10300}
    """
    return {"dimension" : 29, "unit" : 10300}

def LuminousFluxNanolumen():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LuminousFluxNanolumen())
        >>> {"dimension":29,"unit":7344}
    """
    return {"dimension" : 29, "unit" : 7344}

def LuminousIntensityCandela():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LuminousIntensityCandela())
        >>> {"dimension":30,"unit":32736}
    """
    return {"dimension" : 30, "unit" : 32736}

def LuminousIntensityKilocandela():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LuminousIntensityKilocandela())
        >>> {"dimension":30,"unit":12964}
    """
    return {"dimension" : 30, "unit" : 12964}

def LuminousIntensityMegacandela():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LuminousIntensityMegacandela())
        >>> {"dimension":30,"unit":4189}
    """
    return {"dimension" : 30, "unit" : 4189}

def LuminousIntensityGigacandela():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LuminousIntensityGigacandela())
        >>> {"dimension":30,"unit":30038}
    """
    return {"dimension" : 30, "unit" : 30038}

def LuminousIntensityMillicandela():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LuminousIntensityMillicandela())
        >>> {"dimension":30,"unit":13969}
    """
    return {"dimension" : 30, "unit" : 13969}

def LuminousIntensityMicrocandela():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LuminousIntensityMicrocandela())
        >>> {"dimension":30,"unit":32737}
    """
    return {"dimension" : 30, "unit" : 32737}

def LuminousIntensityNanocandela():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(LuminousIntensityNanocandela())
        >>> {"dimension":30,"unit":23767}
    """
    return {"dimension" : 30, "unit" : 23767}

def MagneticFluxWeber():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MagneticFluxWeber())
        >>> {"dimension":31,"unit":5629}
    """
    return {"dimension" : 31, "unit" : 5629}

def MagneticFluxKiloweber():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MagneticFluxKiloweber())
        >>> {"dimension":31,"unit":26282}
    """
    return {"dimension" : 31, "unit" : 26282}

def MagneticFluxMegaweber():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MagneticFluxMegaweber())
        >>> {"dimension":31,"unit":14692}
    """
    return {"dimension" : 31, "unit" : 14692}

def MagneticFluxGigaweber():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MagneticFluxGigaweber())
        >>> {"dimension":31,"unit":21275}
    """
    return {"dimension" : 31, "unit" : 21275}

def MagneticFluxMilliweber():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MagneticFluxMilliweber())
        >>> {"dimension":31,"unit":17139}
    """
    return {"dimension" : 31, "unit" : 17139}

def MagneticFluxMicroweber():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MagneticFluxMicroweber())
        >>> {"dimension":31,"unit":17004}
    """
    return {"dimension" : 31, "unit" : 17004}

def MagneticFluxNanoweber():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MagneticFluxNanoweber())
        >>> {"dimension":31,"unit":14048}
    """
    return {"dimension" : 31, "unit" : 14048}

def MagneticFluxDensityTesla():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MagneticFluxDensityTesla())
        >>> {"dimension":32,"unit":5429}
    """
    return {"dimension" : 32, "unit" : 5429}

def MagneticFluxDensityKilotesla():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MagneticFluxDensityKilotesla())
        >>> {"dimension":32,"unit":26082}
    """
    return {"dimension" : 32, "unit" : 26082}

def MagneticFluxDensityMegatesla():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MagneticFluxDensityMegatesla())
        >>> {"dimension":32,"unit":14492}
    """
    return {"dimension" : 32, "unit" : 14492}

def MagneticFluxDensityGigatesla():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MagneticFluxDensityGigatesla())
        >>> {"dimension":32,"unit":21075}
    """
    return {"dimension" : 32, "unit" : 21075}

def MagneticFluxDensityMillitesla():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MagneticFluxDensityMillitesla())
        >>> {"dimension":32,"unit":16939}
    """
    return {"dimension" : 32, "unit" : 16939}

def MagneticFluxDensityMicrotesla():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MagneticFluxDensityMicrotesla())
        >>> {"dimension":32,"unit":16804}
    """
    return {"dimension" : 32, "unit" : 16804}

def MagneticFluxDensityNanotesla():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MagneticFluxDensityNanotesla())
        >>> {"dimension":32,"unit":13848}
    """
    return {"dimension" : 32, "unit" : 13848}

def MassKilogram():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MassKilogram())
        >>> {"dimension":33,"unit":947}
    """
    return {"dimension" : 33, "unit" : 947}

def MassMetricTon():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MassMetricTon())
        >>> {"dimension":33,"unit":25875}
    """
    return {"dimension" : 33, "unit" : 25875}

def MassGram():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MassGram())
        >>> {"dimension":33,"unit":30108}
    """
    return {"dimension" : 33, "unit" : 30108}

def MassMilligram():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MassMilligram())
        >>> {"dimension":33,"unit":5635}
    """
    return {"dimension" : 33, "unit" : 5635}

def MassMicrogram():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MassMicrogram())
        >>> {"dimension":33,"unit":11586}
    """
    return {"dimension" : 33, "unit" : 11586}

def MassDensityKilogramPerCubicMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MassDensityKilogramPerCubicMeter())
        >>> {"dimension":34,"unit":6936}
    """
    return {"dimension" : 34, "unit" : 6936}

def MassDensityKilogramPerLiter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MassDensityKilogramPerLiter())
        >>> {"dimension":34,"unit":32385}
    """
    return {"dimension" : 34, "unit" : 32385}

def MassDensityGramsPerLiter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MassDensityGramsPerLiter())
        >>> {"dimension":34,"unit":20581}
    """
    return {"dimension" : 34, "unit" : 20581}

def MassDensityGramsPerMilliliter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MassDensityGramsPerMilliliter())
        >>> {"dimension":34,"unit":3214}
    """
    return {"dimension" : 34, "unit" : 3214}

def MassDensityGramsPerCubicCentimeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MassDensityGramsPerCubicCentimeter())
        >>> {"dimension":34,"unit":18887}
    """
    return {"dimension" : 34, "unit" : 18887}

def MassFlowKilogramPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MassFlowKilogramPerSecond())
        >>> {"dimension":35,"unit":235}
    """
    return {"dimension" : 35, "unit" : 235}

def MassFlowGramsPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MassFlowGramsPerSecond())
        >>> {"dimension":35,"unit":3919}
    """
    return {"dimension" : 35, "unit" : 3919}

def MassFlowKilogramPerMinute():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MassFlowKilogramPerMinute())
        >>> {"dimension":35,"unit":30271}
    """
    return {"dimension" : 35, "unit" : 30271}

def MassFlowKilogramPerHour():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MassFlowKilogramPerHour())
        >>> {"dimension":35,"unit":4809}
    """
    return {"dimension" : 35, "unit" : 4809}

def MomentOfInertiaKilogramSquareMeters():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MomentOfInertiaKilogramSquareMeters())
        >>> {"dimension":36,"unit":10408}
    """
    return {"dimension" : 36, "unit" : 10408}

def MomentOfInertiaGramsSquareMeters():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MomentOfInertiaGramsSquareMeters())
        >>> {"dimension":36,"unit":5370}
    """
    return {"dimension" : 36, "unit" : 5370}

def MomentumKilogramPerMetersSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MomentumKilogramPerMetersSecond())
        >>> {"dimension":37,"unit":30354}
    """
    return {"dimension" : 37, "unit" : 30354}

def MomentumGramsPerMetersSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MomentumGramsPerMetersSecond())
        >>> {"dimension":37,"unit":11710}
    """
    return {"dimension" : 37, "unit" : 11710}

def MomentumGramsPerCentimetersSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MomentumGramsPerCentimetersSecond())
        >>> {"dimension":37,"unit":29543}
    """
    return {"dimension" : 37, "unit" : 29543}

def MomentumKilogramPerMetersMinute():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MomentumKilogramPerMetersMinute())
        >>> {"dimension":37,"unit":27623}
    """
    return {"dimension" : 37, "unit" : 27623}

def MomentumKilogramPerKilometersHour():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(MomentumKilogramPerKilometersHour())
        >>> {"dimension":37,"unit":22620}
    """
    return {"dimension" : 37, "unit" : 22620}

def PermeabilityNewtonsPerAmpereSquared():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PermeabilityNewtonsPerAmpereSquared())
        >>> {"dimension":38,"unit":9661}
    """
    return {"dimension" : 38, "unit" : 9661}

def PermeabilityKilonewtonsPerAmpereSquared():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PermeabilityKilonewtonsPerAmpereSquared())
        >>> {"dimension":38,"unit":16255}
    """
    return {"dimension" : 38, "unit" : 16255}

def PermeabilityMeganewtonsPerAmpereSquared():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PermeabilityMeganewtonsPerAmpereSquared())
        >>> {"dimension":38,"unit":123}
    """
    return {"dimension" : 38, "unit" : 123}

def PermeabilityGiganewtonsPerAmpereSquared():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PermeabilityGiganewtonsPerAmpereSquared())
        >>> {"dimension":38,"unit":1639}
    """
    return {"dimension" : 38, "unit" : 1639}

def PermeabilityMillinewtonsPerAmpereSquared():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PermeabilityMillinewtonsPerAmpereSquared())
        >>> {"dimension":38,"unit":31216}
    """
    return {"dimension" : 38, "unit" : 31216}

def PermeabilityMicronewtonsPerAmpereSquared():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PermeabilityMicronewtonsPerAmpereSquared())
        >>> {"dimension":38,"unit":13626}
    """
    return {"dimension" : 38, "unit" : 13626}

def PermeabilityNanonewtonsPerAmpereSquared():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PermeabilityNanonewtonsPerAmpereSquared())
        >>> {"dimension":38,"unit":14182}
    """
    return {"dimension" : 38, "unit" : 14182}

def PermittivityFaradsPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PermittivityFaradsPerMeter())
        >>> {"dimension":39,"unit":11276}
    """
    return {"dimension" : 39, "unit" : 11276}

def PermittivityKilofaradsPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PermittivityKilofaradsPerMeter())
        >>> {"dimension":39,"unit":9638}
    """
    return {"dimension" : 39, "unit" : 9638}

def PermittivityMegafaradsPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PermittivityMegafaradsPerMeter())
        >>> {"dimension":39,"unit":12233}
    """
    return {"dimension" : 39, "unit" : 12233}

def PermittivityGigafaradsPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PermittivityGigafaradsPerMeter())
        >>> {"dimension":39,"unit":10116}
    """
    return {"dimension" : 39, "unit" : 10116}

def PermittivityMillifaradsPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PermittivityMillifaradsPerMeter())
        >>> {"dimension":39,"unit":5094}
    """
    return {"dimension" : 39, "unit" : 5094}

def PermittivityMicrofaradsPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PermittivityMicrofaradsPerMeter())
        >>> {"dimension":39,"unit":12365}
    """
    return {"dimension" : 39, "unit" : 12365}

def PermittivityNanofaradsPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PermittivityNanofaradsPerMeter())
        >>> {"dimension":39,"unit":13983}
    """
    return {"dimension" : 39, "unit" : 13983}

def PlaneAngleRadian():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PlaneAngleRadian())
        >>> {"dimension":40,"unit":14482}
    """
    return {"dimension" : 40, "unit" : 14482}

def PlaneAngleDegree():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PlaneAngleDegree())
        >>> {"dimension":40,"unit":27894}
    """
    return {"dimension" : 40, "unit" : 27894}

def PlaneAngleMinute():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PlaneAngleMinute())
        >>> {"dimension":40,"unit":19598}
    """
    return {"dimension" : 40, "unit" : 19598}

def PlaneAngleSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PlaneAngleSecond())
        >>> {"dimension":40,"unit":22329}
    """
    return {"dimension" : 40, "unit" : 22329}

def PlaneAngleRevolution():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PlaneAngleRevolution())
        >>> {"dimension":40,"unit":21131}
    """
    return {"dimension" : 40, "unit" : 21131}

def PowerWatt():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PowerWatt())
        >>> {"dimension":41,"unit":30182}
    """
    return {"dimension" : 41, "unit" : 30182}

def PowerKilowatt():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PowerKilowatt())
        >>> {"dimension":41,"unit":1021}
    """
    return {"dimension" : 41, "unit" : 1021}

def PowerMegawatt():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PowerMegawatt())
        >>> {"dimension":41,"unit":18541}
    """
    return {"dimension" : 41, "unit" : 18541}

def PowerGigawatt():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PowerGigawatt())
        >>> {"dimension":41,"unit":4838}
    """
    return {"dimension" : 41, "unit" : 4838}

def PowerMilliwatt():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PowerMilliwatt())
        >>> {"dimension":41,"unit":5709}
    """
    return {"dimension" : 41, "unit" : 5709}

def PowerMicrowatt():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PowerMicrowatt())
        >>> {"dimension":41,"unit":11660}
    """
    return {"dimension" : 41, "unit" : 11660}

def PowerNanowatt():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PowerNanowatt())
        >>> {"dimension":41,"unit":12563}
    """
    return {"dimension" : 41, "unit" : 12563}

def PressurePascal():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PressurePascal())
        >>> {"dimension":42,"unit":32306}
    """
    return {"dimension" : 42, "unit" : 32306}

def PressureKilopascal():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PressureKilopascal())
        >>> {"dimension":42,"unit":25752}
    """
    return {"dimension" : 42, "unit" : 25752}

def PressureMegapascal():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PressureMegapascal())
        >>> {"dimension":42,"unit":3639}
    """
    return {"dimension" : 42, "unit" : 3639}

def PressureGigapascal():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PressureGigapascal())
        >>> {"dimension":42,"unit":24284}
    """
    return {"dimension" : 42, "unit" : 24284}

def PressureMillipascal():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PressureMillipascal())
        >>> {"dimension":42,"unit":18832}
    """
    return {"dimension" : 42, "unit" : 18832}

def PressureMicropascal():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PressureMicropascal())
        >>> {"dimension":42,"unit":14433}
    """
    return {"dimension" : 42, "unit" : 14433}

def PressureNanopascal():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PressureNanopascal())
        >>> {"dimension":42,"unit":15154}
    """
    return {"dimension" : 42, "unit" : 15154}

def PressureBar():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PressureBar())
        >>> {"dimension":42,"unit":30666}
    """
    return {"dimension" : 42, "unit" : 30666}

def PressureAtmosphere():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PressureAtmosphere())
        >>> {"dimension":42,"unit":28576}
    """
    return {"dimension" : 42, "unit" : 28576}

def PressurePsi():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(PressurePsi())
        >>> {"dimension":42,"unit":13730}
    """
    return {"dimension" : 42, "unit" : 13730}

def ReluctanceAmpereTurnsPerWeber():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ReluctanceAmpereTurnsPerWeber())
        >>> {"dimension":43,"unit":16495}
    """
    return {"dimension" : 43, "unit" : 16495}

def ReluctanceKiloampereTurnsPerWeber():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ReluctanceKiloampereTurnsPerWeber())
        >>> {"dimension":43,"unit":19097}
    """
    return {"dimension" : 43, "unit" : 19097}

def ReluctanceMegaampereTurnsPerWeber():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ReluctanceMegaampereTurnsPerWeber())
        >>> {"dimension":43,"unit":17583}
    """
    return {"dimension" : 43, "unit" : 17583}

def ReluctanceGigaampereTurnsPerWeber():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ReluctanceGigaampereTurnsPerWeber())
        >>> {"dimension":43,"unit":2322}
    """
    return {"dimension" : 43, "unit" : 2322}

def ReluctanceMilliampereTurnsPerWeber():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ReluctanceMilliampereTurnsPerWeber())
        >>> {"dimension":43,"unit":17462}
    """
    return {"dimension" : 43, "unit" : 17462}

def ReluctanceMicroampereTurnsPerWeber():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ReluctanceMicroampereTurnsPerWeber())
        >>> {"dimension":43,"unit":22198}
    """
    return {"dimension" : 43, "unit" : 22198}

def ReluctanceNanoampereTurnsPerWeber():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ReluctanceNanoampereTurnsPerWeber())
        >>> {"dimension":43,"unit":20134}
    """
    return {"dimension" : 43, "unit" : 20134}

def ResistanceOhm():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ResistanceOhm())
        >>> {"dimension":44,"unit":12282}
    """
    return {"dimension" : 44, "unit" : 12282}

def ResistanceKiloohm():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ResistanceKiloohm())
        >>> {"dimension":44,"unit":8420}
    """
    return {"dimension" : 44, "unit" : 8420}

def ResistanceMegaohm():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ResistanceMegaohm())
        >>> {"dimension":44,"unit":28812}
    """
    return {"dimension" : 44, "unit" : 28812}

def ResistanceGigaohm():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ResistanceGigaohm())
        >>> {"dimension":44,"unit":7546}
    """
    return {"dimension" : 44, "unit" : 7546}

def ResistanceMilliohm():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ResistanceMilliohm())
        >>> {"dimension":44,"unit":8564}
    """
    return {"dimension" : 44, "unit" : 8564}

def ResistanceMicroohm():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ResistanceMicroohm())
        >>> {"dimension":44,"unit":26617}
    """
    return {"dimension" : 44, "unit" : 26617}

def ResistanceNanoohm():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ResistanceNanoohm())
        >>> {"dimension":44,"unit":27635}
    """
    return {"dimension" : 44, "unit" : 27635}

def ResistivityOhmMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ResistivityOhmMeter())
        >>> {"dimension":45,"unit":31052}
    """
    return {"dimension" : 45, "unit" : 31052}

def ResistivityKiloohmMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ResistivityKiloohmMeter())
        >>> {"dimension":45,"unit":27763}
    """
    return {"dimension" : 45, "unit" : 27763}

def ResistivityMegaohmMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ResistivityMegaohmMeter())
        >>> {"dimension":45,"unit":7929}
    """
    return {"dimension" : 45, "unit" : 7929}

def ResistivityGigaohmMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ResistivityGigaohmMeter())
        >>> {"dimension":45,"unit":10909}
    """
    return {"dimension" : 45, "unit" : 10909}

def ResistivityMilliohmMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ResistivityMilliohmMeter())
        >>> {"dimension":45,"unit":9274}
    """
    return {"dimension" : 45, "unit" : 9274}

def ResistivityMicroohmMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ResistivityMicroohmMeter())
        >>> {"dimension":45,"unit":470}
    """
    return {"dimension" : 45, "unit" : 470}

def ResistivityNanoohmMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(ResistivityNanoohmMeter())
        >>> {"dimension":45,"unit":27365}
    """
    return {"dimension" : 45, "unit" : 27365}

def SurfaceDensityKilogramPerSquareMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(SurfaceDensityKilogramPerSquareMeter())
        >>> {"dimension":46,"unit":678}
    """
    return {"dimension" : 46, "unit" : 678}

def SurfaceDensityGramPerSquareMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(SurfaceDensityGramPerSquareMeter())
        >>> {"dimension":46,"unit":28404}
    """
    return {"dimension" : 46, "unit" : 28404}

def SurfaceTensionNewtonPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(SurfaceTensionNewtonPerMeter())
        >>> {"dimension":47,"unit":21802}
    """
    return {"dimension" : 47, "unit" : 21802}

def SurfaceTensionKilonewtonPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(SurfaceTensionKilonewtonPerMeter())
        >>> {"dimension":47,"unit":20164}
    """
    return {"dimension" : 47, "unit" : 20164}

def SurfaceTensionMeganewtonPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(SurfaceTensionMeganewtonPerMeter())
        >>> {"dimension":47,"unit":22759}
    """
    return {"dimension" : 47, "unit" : 22759}

def SurfaceTensionGiganewtonPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(SurfaceTensionGiganewtonPerMeter())
        >>> {"dimension":47,"unit":20642}
    """
    return {"dimension" : 47, "unit" : 20642}

def SurfaceTensionMillinewtonPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(SurfaceTensionMillinewtonPerMeter())
        >>> {"dimension":47,"unit":15620}
    """
    return {"dimension" : 47, "unit" : 15620}

def SurfaceTensionMicronewtonPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(SurfaceTensionMicronewtonPerMeter())
        >>> {"dimension":47,"unit":22891}
    """
    return {"dimension" : 47, "unit" : 22891}

def SurfaceTensionNanonewtonPerMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(SurfaceTensionNanonewtonPerMeter())
        >>> {"dimension":47,"unit":24513}
    """
    return {"dimension" : 47, "unit" : 24513}

def VelocityMetersPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(VelocityMetersPerSecond())
        >>> {"dimension":48,"unit":8336}
    """
    return {"dimension" : 48, "unit" : 8336}

def VelocityKilometersPerHour():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(VelocityKilometersPerHour())
        >>> {"dimension":48,"unit":26130}
    """
    return {"dimension" : 48, "unit" : 26130}

def TemperatureKelvin():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TemperatureKelvin())
        >>> {"dimension":49,"unit":31101}
    """
    return {"dimension" : 49, "unit" : 31101}

def TemperatureCelsius():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TemperatureCelsius())
        >>> {"dimension":49,"unit":20418}
    """
    return {"dimension" : 49, "unit" : 20418}

def TimeSeconds():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TimeSeconds())
        >>> {"dimension":50,"unit":16086}
    """
    return {"dimension" : 50, "unit" : 16086}

def TimeHour():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TimeHour())
        >>> {"dimension":50,"unit":30676}
    """
    return {"dimension" : 50, "unit" : 30676}

def TimeMinutes():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TimeMinutes())
        >>> {"dimension":50,"unit":24272}
    """
    return {"dimension" : 50, "unit" : 24272}

def TimeNanoseconds():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TimeNanoseconds())
        >>> {"dimension":50,"unit":7117}
    """
    return {"dimension" : 50, "unit" : 7117}

def TimeMicroseconds():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TimeMicroseconds())
        >>> {"dimension":50,"unit":16087}
    """
    return {"dimension" : 50, "unit" : 16087}

def TimeMilliseconds():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TimeMilliseconds())
        >>> {"dimension":50,"unit":30086}
    """
    return {"dimension" : 50, "unit" : 30086}

def TimeDay():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TimeDay())
        >>> {"dimension":50,"unit":84}
    """
    return {"dimension" : 50, "unit" : 84}

def TimeWeek():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TimeWeek())
        >>> {"dimension":50,"unit":1267}
    """
    return {"dimension" : 50, "unit" : 1267}

def TimeMonth():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TimeMonth())
        >>> {"dimension":50,"unit":20559}
    """
    return {"dimension" : 50, "unit" : 20559}

def TimeYear():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TimeYear())
        >>> {"dimension":50,"unit":7482}
    """
    return {"dimension" : 50, "unit" : 7482}

def TimeDecade():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TimeDecade())
        >>> {"dimension":50,"unit":29435}
    """
    return {"dimension" : 50, "unit" : 29435}

def TimeCentury():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TimeCentury())
        >>> {"dimension":50,"unit":16414}
    """
    return {"dimension" : 50, "unit" : 16414}

def TorqueNewtonMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TorqueNewtonMeter())
        >>> {"dimension":51,"unit":32088}
    """
    return {"dimension" : 51, "unit" : 32088}

def TorqueKilonewtonMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TorqueKilonewtonMeter())
        >>> {"dimension":51,"unit":16861}
    """
    return {"dimension" : 51, "unit" : 16861}

def TorqueMeganewtonMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TorqueMeganewtonMeter())
        >>> {"dimension":51,"unit":18714}
    """
    return {"dimension" : 51, "unit" : 18714}

def TorqueGiganewtonMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TorqueGiganewtonMeter())
        >>> {"dimension":51,"unit":9363}
    """
    return {"dimension" : 51, "unit" : 9363}

def TorqueMillinewtonMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TorqueMillinewtonMeter())
        >>> {"dimension":51,"unit":3120}
    """
    return {"dimension" : 51, "unit" : 3120}

def TorqueMicronewtonMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TorqueMicronewtonMeter())
        >>> {"dimension":51,"unit":18342}
    """
    return {"dimension" : 51, "unit" : 18342}

def TorqueNanonewtonMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(TorqueNanonewtonMeter())
        >>> {"dimension":51,"unit":14977}
    """
    return {"dimension" : 51, "unit" : 14977}

def VolumeCubicMeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(VolumeCubicMeter())
        >>> {"dimension":52,"unit":9563}
    """
    return {"dimension" : 52, "unit" : 9563}

def VolumeCubicKilometer():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(VolumeCubicKilometer())
        >>> {"dimension":52,"unit":25158}
    """
    return {"dimension" : 52, "unit" : 25158}

def VolumeCubicCentimeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(VolumeCubicCentimeter())
        >>> {"dimension":52,"unit":6770}
    """
    return {"dimension" : 52, "unit" : 6770}

def VolumeCubicMillimeter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(VolumeCubicMillimeter())
        >>> {"dimension":52,"unit":28160}
    """
    return {"dimension" : 52, "unit" : 28160}

def VolumeLiter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(VolumeLiter())
        >>> {"dimension":52,"unit":1279}
    """
    return {"dimension" : 52, "unit" : 1279}

def VolumeMilliliter():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(VolumeMilliliter())
        >>> {"dimension":52,"unit":12789}
    """
    return {"dimension" : 52, "unit" : 12789}

def VolumetricFlowCubicMetersPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(VolumetricFlowCubicMetersPerSecond())
        >>> {"dimension":53,"unit":19359}
    """
    return {"dimension" : 53, "unit" : 19359}

def VolumetricFlowLitersPerSecond():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(VolumetricFlowLitersPerSecond())
        >>> {"dimension":53,"unit":4615}
    """
    return {"dimension" : 53, "unit" : 4615}

def VolumetricFlowLitersPerMinute():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(VolumetricFlowLitersPerMinute())
        >>> {"dimension":53,"unit":1884}
    """
    return {"dimension" : 53, "unit" : 1884}

def VolumetricFlowLitersPerHour():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(VolumetricFlowLitersPerHour())
        >>> {"dimension":53,"unit":28312}
    """
    return {"dimension" : 53, "unit" : 28312}

def InductanceHenry():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(InductanceHenry())
        >>> {"dimension":54,"unit":22799}
    """
    return {"dimension" : 54, "unit" : 22799}

def InductanceKilohenry():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(InductanceKilohenry())
        >>> {"dimension":54,"unit":10685}
    """
    return {"dimension" : 54, "unit" : 10685}

def InductanceMegahenry():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(InductanceMegahenry())
        >>> {"dimension":54,"unit":31862}
    """
    return {"dimension" : 54, "unit" : 31862}

def InductanceGigahenry():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(InductanceGigahenry())
        >>> {"dimension":54,"unit":5678}
    """
    return {"dimension" : 54, "unit" : 5678}

def InductanceMillihenry():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(InductanceMillihenry())
        >>> {"dimension":54,"unit":1542}
    """
    return {"dimension" : 54, "unit" : 1542}

def InductanceMicrohenry():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(InductanceMicrohenry())
        >>> {"dimension":54,"unit":1407}
    """
    return {"dimension" : 54, "unit" : 1407}

def InductanceNanohenry():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(InductanceNanohenry())
        >>> {"dimension":54,"unit":31218}
    """
    return {"dimension" : 54, "unit" : 31218}

def NumericNumber():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(NumericNumber())
        >>> {"dimension":55,"unit":17024}
    """
    return {"dimension" : 55, "unit" : 17024}

def DimensionlessUnknownUnit():
    """
    Helper function to help creating a measure body when inserting messages into the database
    Returns:
        A JSON object
    Example:
        >>> print(DimensionlessUnknownUnit())
        >>> {"dimension":-1,"unit":-1}
    """
    return {"dimension" : -1, "unit" : -1}
