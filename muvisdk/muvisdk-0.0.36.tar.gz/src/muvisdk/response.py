def ok(response, status_code=200):
    return {
        'status': status_code,
        'response': response
    }


def error(response, status_code=400):
    return {
        'status': status_code,
        'response': response
    }
