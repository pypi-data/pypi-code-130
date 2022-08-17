class DataFrame :
    def __init__(self):        
        super().__init__()

    def __new__(cls):        
        return super().__new__(cls)
    
    def test(self) :
        return "DataFrame Test."