import ky3m.methods
from ky3m import methods
from ky3m.common.latin import *


# methods.py adapter
def use_method(_input_data):
    report = None

    # "m" := "method"
    m_fields = _input_data.split(' ')
    m_name = m_fields[0]

    # specification definition
    try:
        m_spec = m_fields[1:]
    except IndexError:  # if no spec. provided
        m_spec = []

    try:
        if m_name.casefold() in dir(methods):  # check for method existence
            m = getattr(methods, m_name.casefold())
            report = m(tuple(m_spec))  # method call, report.Report class returned
            if report is None:
                print('Nothing to report!')
            else:
                print(report)
        else:
            print(f'Method {m_name} does not exist!')
    except ky3m.methods.InvalidSpecification:
        print(f'Method {m_name} accepts a different specification format!')
    except NotImplementedError:
        print(f'Method {m_name} is not implemented!')

    return report


# developer function
def use_method_adv(_input_data):
    report = use_method(_input_data)

    # check log for presence
    if report:
        log = ''
        for record in report.log:
            log += record + '\n'
        print(f'\nLog intercepted:\n{log}')
    else:
        pass


# help output
def help_output():
    print(f"""\
See project's README: https://github.com/Procybit/Ky3M/blob/latest/README.md

These are Ky3M CLI commands:
(windows command-line syntax key is used;
for more info see
    https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/command-line-syntax-key)
("mods folder" is your minecraft mods folder that located at path like
    "%APPDATA%\\.minecraft\\mods" or "~/.minecraft/mods")
("local library" is place where Ky3M saves all its files; it located at
    path like "%LOCALAPPDATA%\\_Ky\\3M" or "~/.ky3m/")
("bundle" is an analogue of the modpack for Minecraft but it created by Ky3M)

Service commands (case-fold):
help
    ↑ shows this message

Methods (uppercase):
INSPECT
    ↑ shows all .jar files stored in mods folder;
    ↑ generates "listed id" used by methods below for every listed .jar file ("INSPECT use" local);
    ↑ overwrites all "listed id"s generated before;
PEER <listed id>
    ↑ shows detailed info about specific .jar file in mods folder;
EXPEL <listed id>
    ↑ permanently deletes specific .jar file from mods folder;
ADOPT <listed id>
    ↑ saves specific .jar file into local library;
    ↑ generates "saved id" used by methods below for every saved .jar file (local library local);
ADOPTS
    ↑ shows all .jar files saved into local library before;
RELEASE <saved id>
    ↑ releases (copies) certain .jar file from local library to mods folder;
PUNISH <saved id>
    ↑ permanently deletes specific .jar file saved into local library before;
    ↑ note that using PUNISH on binded to any bundle .jar files mean they will be no longer available to these bundles;
BUNDLE <bundle id> | <bundle name>
    ↑ checks if the specified "bundle id" is in UUID format and tries to output its bundle info;
    ↑ on failure creates new bundle with the specified "bundle name" name;
    ↑ generates "bundle id" used by itself and by methods below for every created bundle (local library local);
BUNDLES
    ↑ shows all bundles created before;
BURST <bundle id>
    ↑ permanently deletes specific bundle;
BIND <bundle id> <saved id>
    ↑ binds specific .jar file saved in local library before;
    ↑ generates "bind id" used by methods below for every binded .jar file (bundle local);
DETACH <bundle id> <bind id>
    ↑ unbinds specific .jar file;
APPLY <bundle id>
    ↑ releases binded to specific bundle .jar files saved to local library before;
""")


def main():
    while True:
        print('\nKy3M :> ', end='')
        input_data = input().strip()

        # for METHODS (if first word is capitalized)
        if all(char in latin_upper for char in input_data.split(' ')[0]):
            use_method(input_data)

        # for METHODS (for developers)
        elif (all(char in latin_upper for char in input_data[3:].strip().split(' ')[0]) and
              input_data.split(' ')[0][:3] == 'adv'):
            use_method_adv(input_data[3:])

        elif input_data.strip().casefold() == 'help':
            help_output()

        else:
            print('Unknown syntax or command!')


if __name__ == '__main__':
    main()
