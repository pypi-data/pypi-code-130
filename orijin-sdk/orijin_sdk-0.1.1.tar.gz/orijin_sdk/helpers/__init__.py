import requests
from requests import Response

#region: Image Uploading
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
            '0': ("0", upload_file, "image/jpeg")
        }

        response = requests.post(url=endpoint, headers=headers, files=form)

        return(response.text)
#endregion

def log_request(r: Response, filename: str = 'temp/request.log'):
    """For debugging only.  This will save the request details to a log file for you to review."""
    with open(filename,'w') as request_file:
        request_file.write('{}\n{}\r\n{}\r\n\r\n{}'.format(
            '-----------START-----------',
            r.request.method + ' ' + r.request.url,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in r.request.headers.items()),
            r.request.body,
        ))