import argparse
import configparser

from tele_upload.main import setup, test_token, reset, upload_file, download, config_file

__version__ = "0.0.2"
package_name = "tele-upload"

config = configparser.ConfigParser()
config.read(config_file)
chat_id = config['Telegram']['chat_id']
bot_token = config['Telegram']['bot_token']

example_uses = '''example:
   tele-upload setup
   tele-upload reset
   tele-upload test
   tele-upload up {files_name}
   tele-upload d {urls}'''

def main(argv = None):
	parser = argparse.ArgumentParser(prog=package_name, description="upload your files to your group or channel", epilog=example_uses, formatter_class=argparse.RawDescriptionHelpFormatter)
	subparsers = parser.add_subparsers(dest="command")

	setup_parser = subparsers.add_parser("setup", help="setup your telegram credentials")

	reset_parser = subparsers.add_parser("reset", help="reset to default your telegram credentials")

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
	elif args.command == "reset":
		return reset()
	elif args.command == "up":
		return upload_file(bot_token, chat_id, args.filename)
	elif args.command == "d":
		return download(args.url)
	elif args.version:
		return print(__version__)
	else:
		parser.print_help()

if __name__ == '__main__':
	raise SystemExit(main())