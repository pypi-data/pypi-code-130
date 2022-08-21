import re
import appdirs
from pathlib import Path
import shutil
import json
import sys

CONFIG_DIR = Path(appdirs.user_config_dir(appname='regex-application'))
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
HARD_SAVE_DIR = CONFIG_DIR / 'hard-save'
HARD_SAVE_DIR.mkdir(parents=True, exist_ok=True)

RE_START = 'mt '
SU_START = 'su '
POSSIBLE_STARTS = [
    RE_START,
    SU_START
]

# import readline

# def completer(text, state):
#     parser = get_cli_parser()
#     print (text)
#     return 'patata'
#     # options = [i for i in commands if i.startswith(text)]
#     # if state < len(options):
#     #     return options[state]
#     # else:
#     #     return None

# readline.parse_and_bind("tab: complete")
# readline.set_completer(completer)

class Config:
    def __init__(self, config=None):
        if config is None:
            config = {}
        self.config = config
    
    def add_config(self, path:Path, soft:bool):
        if not soft:
            path = shutil.copyfile(str(path), str(HARD_SAVE_DIR / path.name))
            path = Path(path)
        self.config[str(path.stem)] = str(path)

    def to_file(self, path):
        with open(str(path), 'w+') as f:
            json.dump(self.config, f)

    @staticmethod
    def from_file(path):
        with open(str(path), 'r') as r:
            try:
                config = json.load(r)
            except Exception:
                raise TypeError(f'Error loading config from {path}')
            return Config(config=config)

class ConfigManager:

    CONFIG_PATH = CONFIG_DIR / 'settings.json'
        
    @staticmethod
    def get_config():
        
        if not ConfigManager.CONFIG_PATH.is_file():
            config = Config()
            config.to_file(ConfigManager.CONFIG_PATH)
        return Config.from_file(ConfigManager.CONFIG_PATH)
    
    @staticmethod
    def save_config(config: Config):
        return config.to_file(ConfigManager.CONFIG_PATH)
        

class RegexStep:
    def __init__(self, match:str, subs:str):
        self.match :re.Pattern = re.compile(match)
        self.subs :str = subs
    
    def sub(self, content):
        return self.match.sub(self.subs, content)

    def __str__(self):
        return f'<RegexStep match: {self.match}; subs: {self.subs}'
    
    def __repr__(self):
        return str(self)


def get_parser(path):
    with open(path, 'r') as f:
        lines = f.read().splitlines()
    
    steps = []
    mt = None
    for line in lines:
        line = line.lstrip()
        line = line.rstrip('\n').rstrip('\r')
        if not line or line.startswith('#'):
            continue
        if line.startswith(RE_START):
            line = line[len(RE_START):]
            if mt is not None:
                raise ValueError(f'Found regex {mt} without substitution')
            mt = line
        elif line.startswith(SU_START):
            line = line[len(SU_START):]
            if mt is None:
                raise ValueError(f'Found {line} without matching regex')
            step = RegexStep(mt, line)
            steps.append(step)
            mt = None
        else:
            raise ValueError(f'Unexpected line: {line}. Expected line that starts with: {POSSIBLE_STARTS}')
    return steps

def run(args):
    r = args.regex
    re_path = Path(r)
    if not re_path.is_file():
        config = ConfigManager.get_config()
        re_path = config.config.get(r, None)
        if re_path is None or not Path(re_path).is_file():
            raise ValueError(f'Regex file: {r}; not found in filesystem or saved in DB')
        re_path = Path(re_path)
    steps = get_parser(re_path)
    args.source.resolve(strict=True)
    with open(args.source, 'r') as f:
        content = f.read()
    for step in steps:
        content = step.sub(content)
    print(content, end='')
    # print(steps)

def save(path, soft):
    config = ConfigManager.get_config()
    config.add_config(Path(path), soft)
    ConfigManager.save_config(config)

def list_regex():
    config = ConfigManager.get_config()
    for id, path in config.config.items():
        print(id, path)

def get_cli_parser():
    import argparse

    parser = argparse.ArgumentParser(prog='rega', description='Apply regex in bulk')
    parser.add_argument('regex', type=str, nargs='?', help='Path to the regex file OR name of the saved regex file')
    parser.add_argument('source', type=Path, nargs='?', default=None, help='Path to the source file for processing')
    parser.add_argument('--save', action='store_true', help='Save (copying the full file!) the regex application file')
    parser.add_argument('--save-soft', action='store_true', help='Save (saving the path to the file!) the regex application file')
    parser.add_argument('--list', action='store_true', help='List all saved regex files')
    return parser

def main():
    parser = get_cli_parser()
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    if args.list:
        list_regex()
    elif args.save or args.save_soft:
        if args.save and args.save_soft:
            raise ValueError('Cannot save hard and soft at the same time')
        save(args.regex, args.save_soft)
    else:
        run(args)

if __name__ == '__main__':
    main()