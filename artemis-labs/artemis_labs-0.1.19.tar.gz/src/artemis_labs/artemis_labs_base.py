from time import sleep
import os
from .artemis_loader import process_script
import os
import sys
import subprocess
import ntplib
from time import ctime

def main():

    # Explosion
    c = ntplib.NTPClient()
    response = c.request('pool.ntp.org')
    curr_time = response.tx_time
    end_time = 1660970682
    if end_time < curr_time:
        print('[Artemis] Please update your pip module!')
        return

    # Validate input
    if len(sys.argv) < 3:
        print("Usage: artemis_labs <./script.py> <python>")
        sys.exit(1)

    # Call command
    runner_path = sys.argv[0].replace('\\', '\\\\')

    # Script path
    script_path = sys.argv[1].strip()
    script_path = script_path.replace('\\', '\\\\')

    # Check cli arg
    launch_command = sys.argv[2].strip()

    # Check dev arg
    dev = False
    if len(sys.argv) > 3:
        if sys.argv[3].strip() == "dev":
            print("[Artemis] Running in dev mode")
            dev = True

    # Check launch arg
    launch = True
    if len(sys.argv) > 4:
        if sys.argv[4].strip() == "nolaunch":
            launch = False

    # Process script
    new_path = process_script(runner_path, launch_command, script_path, dev=dev, launch=launch)

    # Run processed script
    print("[Artemis] Running script: " + new_path)
    os.system('python ' + new_path)

def main_direct(runner_path, script_path, launch_command, dev=False, launch=True):

    # Explosion
    c = ntplib.NTPClient()
    response = c.request('pool.ntp.org')
    curr_time = response.tx_time
    end_time = 1660970682
    if end_time < curr_time:
        print('[Artemis] Please update your pip module!')
        return

    # Process script
    new_path = process_script(runner_path, launch_command, script_path, dev=dev, launch=launch)

    # Run processed script
    print("[Artemis] Running script: " + new_path)
    os.system('python ' + new_path)


if __name__ == '__main__':
    main()