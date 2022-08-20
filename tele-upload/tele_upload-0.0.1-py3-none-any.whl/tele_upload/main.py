import requests
import configparser
import tqdm
import requests_toolbelt
import sys
import argparse
import os

__version__ = "0.0.1"
package_name = "tele-upload"

base_dir = os.path.dirname(os.path.realpath(__file__))
config_file = os.path.join(base_dir, 'config.ini')

class ProgressBar(tqdm.tqdm):
    def update_to(self, n: int) -> None:
        self.update(n - self.n)

def setup():
	config = configparser.ConfigParser()
	config.read(config_file)
	print('If you did not want change anyone, just press enter.')
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

	print("Config file has been reset!")	

config = configparser.ConfigParser()
config.read(config_file)
chat_id = config['Telegram']['chat_id']
bot_token = config['Telegram']['bot_token']

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

def uploadd_file(bot_token:str, chat_id:str, file_name:str):

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

example_uses = '''example:
   tele-upload setup
   tele-upload up {files_name}
   tele-upload d {urls}'''

def main(argv = None):
    parser = argparse.ArgumentParser(prog=package_name, description="upload your files to your group or channel", epilog=example_uses, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command")

    setup_parser = subparsers.add_parser("setup", help="setup your telegram credentials")

    reset_parser = subparsers.add_parser("setup", help="reset your telegram credentials")

    test_parser = subparsers.add_parser("test", help="test telegram bot token")

    upload_parser = subparsers.add_parser("up", help="upload file to your group or channel")
    upload_parser.add_argument("filename", type=str, help="one or more files to upload")

    download_parser = subparsers.add_parser("d", help="download files ")
    download_parser.add_argument("url", type=str, help="download and upload file to your group or channel")

    parser.add_argument('-v',"--version",
                            action="store_true",
                            dest="version",
                            help="check version of tele-upload")

    args = parser.parse_args(argv)

    if args.command == "test":
    	return test_token(bot_token)
    elif args.command == "setup":
    	return setup()
    elif args.command == "setup":
    	return reset()
    elif args.command == "up":
        return uploadd_file(bot_token, chat_id, args.filename)
    elif args.command == "d":
        return download(args.url)
    elif args.version:
        return print(__version__)
    else:
        parser.print_help()

if __name__ == '__main__':
    raise SystemExit(main())