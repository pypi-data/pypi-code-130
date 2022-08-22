import sys
import os
import tqdm
import requests
import configparser
import requests_toolbelt

base_dir = os.path.dirname(os.path.realpath(__file__))
config_file = os.path.join(base_dir, 'config.ini')

class ProgressBar(tqdm.tqdm):
	def update_to(self, n: int) -> None:
		self.update(n - self.n)

def setup():
	config = configparser.ConfigParser()
	config.read(config_file)
	print('If you did not want to change anyone, just press enter.')
	chat_id = input("Enter your channel name or chat id with '-' : ")
	if chat_id != '':
		config.set('Telegram', 'chat_id', chat_id)

	bot_token = input("Enter your telegram bot api token  : ")
	if bot_token != '':
		config.set('Telegram', 'bot_token', bot_token)

	with open(config_file, 'w') as configfile:
		config.write(configfile)

	print("Setup complete!")

def reset():
	config = configparser.ConfigParser()
	config.read(config_file)

	config.set('Telegram', 'chat_id', '@xxxxxxxx')
	config.set('Telegram', 'bot_token', '098765:xxxxxxxxxxxxx')

	with open(config_file, 'w') as configfile:
		config.write(configfile)

	print("Config file has been reset to default!")	

def url(bot_token:str):
	url = f'https://api.telegram.org/bot{bot_token}/getMe'
	return url

def test_token(bot_token:str):
	r = requests.get(url(bot_token))
	verify_data = r.json()

	if verify_data['ok'] == True:
		print(f'Bot Token is correct and Bot username is {verify_data["result"]["username"]}.')
	elif verify_data['ok'] == False:
		print(f'Bot Token is wrong.')

def upload_url(bot_token:str):
	url = f'https://api.telegram.org/bot{bot_token}/sendDocument'
	return url

def upload_file(bot_token:str, chat_id:str, file_name:str):

	file_size = os.path.getsize(file_name)

	if file_size > 51200000:
		sys.exit("Bot can upload only 50 MB file.")
	data_to_send = []
	session = requests.session()

	with open(file_name, "rb") as fp:
		data_to_send.append(
			("document", (file_name, fp))
		)
		data_to_send.append(('chat_id', (chat_id)))
		encoder = requests_toolbelt.MultipartEncoder(data_to_send)
		with ProgressBar(
			total=encoder.len,
			unit="B",
			unit_scale=True,
			unit_divisor=1024,
			miniters=1,
			file=sys.stdout,
		) as bar:
			monitor = requests_toolbelt.MultipartEncoderMonitor(
				encoder, lambda monitor: bar.update_to(monitor.bytes_read)
			)

			r = session.post(
				upload_url(bot_token),
				data=monitor,
				allow_redirects=False,
				headers={"Content-Type": monitor.content_type},
			)

	resp = r.json()
	
	if resp['ok'] == True:
		print(f'{file_name} uploaded sucessfully on {chat_id}')
	else:
		print(resp)
		print("\nThere is something error")

def download(url:str):
	print('This is not working now.')
