import requests
import json
import base64


class PandaError(Exception):


    def __init__(self, message, response=None):
        self.response = response
        self.message = message

    def __str__(self):
        if self.response is not None:
            respose_text = self.response.text
            return f"PandaError({self.message}, response=({self.response.status_code}, {respose_text}))"
        
        return f"PandaError({self.message})"
        

class Panda:


    def __init__(self, autorization_panda_video):
        self.authorization = autorization_panda_video
        self.base_url = "https://api-v2.pandavideo.com.br"
        self.TUS_VERSION = '1.0.0'

    def list_uploader_servers(self):
        url = self.base_url + '/hosts/uploader'
        headers = {
            "Accept": "application/json",
            "Authorization": self.authorization
        }

        response = requests.get(url, headers=headers)

        return json.loads(response.text)

    def mount_url(self, path, **kwargs):
        parameters = [f"{key}={value}" for key, value in kwargs.items()]

        url = self.base_url + path

        if parameters:
            url = (url + "?") + "&".join(parameters)

        return url

    def convert_b64(self, token):
        if not isinstance(token, str):
            raise TypeError('Token deve ser um string')

        return base64.b64encode(token.encode()).decode()
            
class PandaFolder(Panda):


    def list_folders(self, **kwargs):
        url = self.mount_url('/folders', **kwargs)
        headers = {
            "Accept": "application/json",
            "Authorization": self.authorization
        }
        response = requests.get(url, headers=headers)
        return json.loads(response.text)

    def create_folder(self, **kwargs):
        url = self.mount_url('/folders')
        if 'name' not in kwargs.keys():
            raise KeyError('A chave name é obrigatória')
        
        payload = kwargs

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            'authorization': self.authorization
           
        }

        response = requests.post(url, json=payload, headers=headers)
        if not (response.status_code >= 200 and response.status_code <=299):
            raise PandaError('Status code response not is 200', response)
        return json.loads(response.text)

    def update_folder(self, folder_id, **kwargs):
        url = self.mount_url(f'/folders/{folder_id}')
        
        if 'name' not in kwargs.keys():
            raise KeyError('A chave name é obrigatória')

        payload = kwargs
        headers = headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": self.authorization
        }

        response = requests.put(url, json=payload, headers=headers)

        if not (response.status_code >= 200 and response.status_code <=299):
            raise PandaError('Status code response not is 200', response)

        return json.loads(response.text)
        
    def delete_folder(self, folder_id):
        url = self.mount_url(f'/folders/{folder_id}')
        headers = headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": self.authorization
        }
        
        response = requests.delete(url, headers=headers)

        if not (response.status_code >= 200 and response.status_code <=299):
            raise PandaError('Status code response not is 200', response)

        return json.loads(response.text)

class PandaVideo(Panda):


    def list_videos(self, **kwargs):
        url = self.mount_url('/videos', **kwargs)

        headers = {
            "Accept": "application/json",
            "Authorization": self.authorization
        }

        response = requests.get(url, headers=headers)

        if not (response.status_code >= 200 and response.status_code <=299):
            raise PandaError('Status code response not is 200', response)

        return json.loads(response.text)

    def get_video_properties(self, video_id):
        url = self.mount_url(f'/videos/{video_id}')
        
        headers = {
            "Accept": "application/json",
            "Authorization": self.authorization
        }

        response = requests.get(url, headers=headers)

        if not (response.status_code >= 200 and response.status_code <=299):
            raise PandaError('Status code response not is 200', response)

        return json.loads(response.text)

    def update_video_properties(self, video_id, **kwargs):
        url = self.mount_url(f'/videos/{video_id}')

        if not kwargs:
            raise PandaError('Nenhum atributo de alteração foi especificado')

        payload = kwargs

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": self.authorization
        }

        response = requests.put(url, json=payload, headers=headers)

        if not (response.status_code >= 200 and response.status_code <=299):
            raise PandaError('Status code response not is 200', response)

        return json.loads(response.text)

    def upload_video(self, bytes_video, size_video, filename, folder_id, uuid_video):
        #bytes_video = bytes_video.read()
        upload_server = self.list_uploader_servers()['hosts']['us'][1]
        url = "https://" + upload_server + '.pandavideo.com.br/files'
        payload = bytes_video
        headers = {
            'Tus-Resumable': '1.0.0',
            'Upload-Length': str(size_video),
            'Content-Type': 'application/offset+octet-stream',
            'Upload-Metadata': f'authorization {self.convert_b64(self.authorization)},filename {self.convert_b64(filename)},folder_id {self.convert_b64(folder_id)},video_id {self.convert_b64(uuid_video)}'
        }

        response = requests.post(url, headers=headers, data=payload)
        if not (response.status_code >= 200 and response.status_code <=299):
            raise PandaError('Status code response not is 200', response)

        return response.status_code