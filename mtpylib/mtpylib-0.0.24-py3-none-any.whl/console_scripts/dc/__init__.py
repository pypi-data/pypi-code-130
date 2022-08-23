import sys
import os
from mtlibs import process_helper

from dotenv import load_dotenv, find_dotenv
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


def console_script_entry():
    print("命令行参数", sys.argv)
    print("环境变量", os.environ)
    argv = sys.argv
    argv[0] = 'docker-compose'
    print("command",argv)
    
    docker_compose_args = os.environ.get("DOCKER_COMPOSE_ARGS","")
    argv.extend(docker_compose_args)
    result2 = process_helper.exec(' '.join(argv))
    print(result2)