class db :

    def __init__(self): 
        self.types = ['RDS','DynamoDb','Neptune']

    def displayd(self): 
        for t in self.types: 
            print(t)