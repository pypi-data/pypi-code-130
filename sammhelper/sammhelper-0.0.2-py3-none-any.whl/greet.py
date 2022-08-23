from datetime import datetime

def greet():
    time = datetime.now().hour
    if time < 11:
        return "Good Morning!"
    elif time < 15:
        return "Good Afternoon!"
    elif time < 18:
        return "Good Evening!"
    else:
        return "Good Night!"