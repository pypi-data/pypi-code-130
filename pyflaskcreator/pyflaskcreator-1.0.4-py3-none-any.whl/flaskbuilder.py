
import os
import shutil
import argparse


class FlaskCreator:

    def __init__(self):
        self.app_path, self.env_name = self.get_path_from_args()
        self.create_app()


    def get_path_from_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', '--path', help='Path  of the app', required=True, metavar='PATH', default='flaskApp')
        parser.add_argument('-e', '--env', help='Python enviroment name', metavar='ENV', default='env')
        args = parser.parse_args()


        return args.path, args.env


    def build_folder(self, path):
        try:
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                elif os.path.isfile(path):
                    os.remove(path)
            

            os.system(f"mkdir {path}")

        except Exception as e:
            print(f"Error while building new folder\nEXCEPTION: {e}")


    def build_file(self, asset_loc, asset_dest):
        with open(asset_loc, 'rb') as asset_loc_file:
            asset_content = asset_loc_file.read()

        with open(asset_dest, 'wb') as asset_dest_file:
            asset_dest_file.write(asset_content)



    def create_successful(self, element,path):
        if os.path.exists(path):
            print(f"\33[97m[\u001b[32;1m\u2713\33[97m]{element}: \u001b[33;1m{path}\033[0m")
            return 1
        else:
            print(f"THERE WAS A PROBLEM CREATING {element} at {path}")
            quit()

    def create_app(self):

        print(f"\33[97mCREATING APP: \u001b[33;1m{self.app_path} \33[97m\033[5m\u2022 \u2022 \u2022\033[0m ")

        try:
            input("Is this correct?\nPress ctrl+c to cancel or enter to continue...\n")
        except KeyboardInterrupt:
            quit()

        self.build_folder(self.app_path)
        self.create_successful("PATH",self.app_path)
        
        self.build_folder(os.path.join(self.app_path, 'templates'))
        self.create_successful("TEMPLATES", os.path.join(self.app_path, 'templates\\'))


        self.build_folder(os.path.join(self.app_path, 'static'))
        self.create_successful("STATIC",os.path.join(self.app_path, 'static\\'))

        self.build_file(f'{os.path.dirname(__file__)}/assets/app.py', os.path.join(self.app_path, 'app.py'))
        self.create_successful("APP.PY",os.path.join(self.app_path, 'app.py'))

        self.build_file(f'{os.path.dirname(__file__)}/assets/welcome.html', os.path.join(self.app_path, 'templates\\welcome.html'))
        self.create_successful("WELCOME.HTML",os.path.join(self.app_path, 'templates\\welcome.html'))

        self.build_file(f'{os.path.dirname(__file__)}/assets/welcome.css', os.path.join(self.app_path, 'static\\welcome.css'))
        self.create_successful("WELCOME.CSS",os.path.join(self.app_path, 'static\\welcome.css'))

        self.build_file(f'{os.path.dirname(__file__)}/assets/flask_icon.png', os.path.join(self.app_path, 'static\\flask_icon.png'))
        self.create_successful("FLASK ICON",os.path.join(self.app_path, 'static\\flask_icon.png'))

        os.system(f'python -m venv {os.path.join(self.app_path, self.env_name)}')
        self.create_successful("ENV",os.path.join(self.app_path, f"{self.env_name}\\"))

        print("\n\u001b[32;1mAPP CREATED SUCCESSFULLY\033[0m")

def create():
    appCreator = FlaskCreator()


if __name__ == '__main__':
    appCreator = FlaskCreator()

