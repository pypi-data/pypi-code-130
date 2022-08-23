

def trigger(train, validation, inference, refresh=False, save=False):
    return None

def equip(model):
    setattr(model, 'trigger', trigger)
    return model
