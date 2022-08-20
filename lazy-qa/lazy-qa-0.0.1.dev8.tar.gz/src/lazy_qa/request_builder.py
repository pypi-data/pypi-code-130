import gzip
import time
import calendar
import io
import requests
import zlib

# ---------------------------------------------------------------------------------------------------------------------#
#                                       Functions to manipulate API Requests                                           #
# ---------------------------------------------------------------------------------------------------------------------#

# ---------------------------------------------- API Requests Functions -----------------------------------------------#


def response_from_auth(method, url, payload):
    request_trace_id = "TestData-" + method
    headers = {
        'requestTraceId': request_trace_id,
        'Content-Type': 'application/x-www-form-urlencoded',

    }
    response = select_request(method, url, payload, headers)
    if method is not None:
        if response is not None:
            # evaluate_response(payload, response)
            data = response.json()
            return data
        else:
            print("Auth wasn't able to be execute through the method " + str(method) + ". Check your configuration yml "
                                                                                       "and try again.")


def get_access_token(key, method, url, payload):
    print("\nGetting Token Authentication...")
    data = response_from_auth(method, url, payload)
    if key in data:
        token = data[key]
        return str(token)


def zip_payload(payload: str) -> bytes:
    file = io.BytesIO()
    g = gzip.GzipFile(fileobj=file, mode='w')
    if type(payload) is str:
        g.write(bytes(payload, "utf-8"))
    else:
        g.write(payload)
    g.close()
    return file.getvalue()


def print_request_and_exit(method, url, headers, body_request, zip_payload_needed):
    # connection_test()
    print('\n\n*************************** DEBUG MODE ***************************')
    print('                No request made to any endpoint!!!')
    print('Add the -e flag to the command line to really execute the requests')
    print('********************************************************************\n')
    print(f'METHOD: {method}\n')
    print(f'URL: {url}\n')
    print(f'HEADERS: \n\n{headers}\n')
    if type(body_request) is not list:
        unzipped_payload = zlib.decompress(body_request, 16 + zlib.MAX_WBITS) if zip_payload_needed else body_request
        if type(unzipped_payload) is not bytes:
            unzipped_payload = bytearray(unzipped_payload, "utf-8")
        print(f'PAYLOAD: \n\n{unzipped_payload.decode("utf-8")}\n')
    else:
        for req in body_request:
            unzipped_payload = zlib.decompress(req, 16 + zlib.MAX_WBITS) if zip_payload_needed else req
            if type(unzipped_payload) is not bytes:
                unzipped_payload = bytearray(unzipped_payload, "utf-8")
            print(f'PAYLOAD: \n\n{unzipped_payload.decode("utf-8")}\n')


def split(list_a, chunk_size):
    for i in range(0, len(list_a), chunk_size):
        yield list_a[i:i + chunk_size]


def get_multiple_requests(method, url, headers, payload):
    response = []
    chunk_payload = split(payload, 1)
    for idx, e in enumerate(payload):
        if type(headers) is list:
            new_headers = headers[idx]
        else:
            new_headers = headers
        new_headers['requestTraceId'] = f"{new_headers['requestTraceId']}_part_{idx + 1}_of_{len(payload)}"
        new_headers['x-timestamp'] = str(calendar.timegm(time.gmtime()))
        response.append(requests.request(method, url, data=e, headers=new_headers))
    return response


def select_request(method, url, payload, headers, multiple_request=False):
    # This method is responsible for create only one body for method
    if method == "post":
        if multiple_request:
            response = get_multiple_requests(method, url, headers, payload)
        else:
            response = requests.post(url, data=payload, headers=headers, verify=False)
        return response
    elif method == "put":
        if multiple_request:
            response = get_multiple_requests(method, url, headers, payload)
        else:
            response = requests.put(url, data=payload, headers=headers, verify=False)
        return response
    elif method == "delete":
        if multiple_request:
            response = get_multiple_requests(method, url, headers, payload)
        else:
            response = requests.delete(url, data=payload, headers=headers, verify=False)
        return response
    elif method == "get":
        all_responses = []
        for p in payload:
            response = requests.get(url, headers=headers, params=p, verify=False)
            all_responses.append(response)
        return all_responses
    else:
        print("Method " + method + " is not found")
        return None  # 0 is the default case if method is not found
