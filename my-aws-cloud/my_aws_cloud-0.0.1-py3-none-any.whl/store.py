class store:
    
    def __init__(self): 
        self.types = ['S3','Glacier','EBS','EFS']
    
    def displays(self):

        for t in self.types :
            print(t)
