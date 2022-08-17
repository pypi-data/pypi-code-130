import requests

def sendSMS(phone_number,message,sender_id,api_key):
    
    endpoint = "https://roycebulksms.com/api/sendmessage"
    data ={
    'sender_id': sender_id, 'text_message': message, 'phone_number': phone_number
    }

    headers = {
    "Authorization": "Bearer "+api_key
    }

    response=requests.post(endpoint, data=data, headers=headers)

    return response.json()

def deliveryReport(message_id,api_key):
    endpoint = "https://roycebulksms.com/api/delivery-report"
    data ={
    'message_id': message_id
    }

    headers = {
    "Authorization": "Bearer "+api_key
    }

    response=requests.post(endpoint, data=data, headers=headers)

    return response.json()




    