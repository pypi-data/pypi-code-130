import requests

def upload_image(file_path, endpoint, token):
    """Use GQL mutation.fileUpload
    
    Args:
        file_path (string): The path of the file to be uploaded.
    
    Returns:
        name, url
    """
    with open(file_path, 'rb') as upload_file:
        # url = endpoint

        headers = {
            'Authorization': token,
            'Content-Type': 'multipart/form-data',
        }

        form = {
            'operations': (None, "{\"query\": \"mutation ($file: Upload!) {fileUpload(file: $file) {name, url}}\", \"variables\": { \"file\": null }}"),
            'map': (None, "{\"0\":[\"variables.file\"]}"),
            '0': ("0", open(file_path, 'rb'), "image/jpeg")
        }

        response = requests.post(url=endpoint, headers=headers, files=form)

        with open('temp/request.txt','w') as request_file:
            request_file.write('{}\n{}\r\n{}\r\n\r\n{}'.format(
                '-----------START-----------',
                response.request.method + ' ' + response.request.url,
                '\r\n'.join('{}: {}'.format(k, v) for k, v in response.request.headers.items()),
                response.request.body,
            ))

        print(response.text)
