import onepasswd
from onepasswd.onepasswd import PasswdGen
from onepasswd.config import Config
from onepasswd import crypto
from onepasswd.onepasswd import DB
from onepasswd.onepasswd import GitDB
from onepasswd.tools import jmerge, jdiff
import argparse
from onepasswd import ltlog
import sys
import pyperclip
from pathlib import Path
import os
import json
import getpass
import time
import tempfile

log = ltlog.getLogger('onepasswd.client')


class Cmd(object):
    LENGTH = 12
    SELECT = "0aA~"

    def __init__(self):
        self.select = Cmd.SELECT
        self.length = Cmd.LENGTH
        self.charset = None
        self.printpasswd = False
        self.force = False
        self.func = None
        self.config = Config.CONF_PATH
        self.__config = None
        self.user = None
        self.token = None
        self.entry = None
        self.backup_path = None
        self._db = None
        self.query = []
        self.repo = 'onepasswd-db'
        self.enc_passwd = ""
        self.loglevel = "INFO"

    @property
    def _config(self):
        if not self.__config:
            self.__config = Config(self.config)
        return self.__config

    @property
    def db(self):
        if not self._db:
            self._db = DB(self._config['db'])
        return self._db

    def return_password(self, passwd):
        if self.printpasswd:
            print(passwd)
        else:
            pyperclip.copy(passwd)

    def get_password(self):
        log.debug("trace " + "get_password")
        if self.printpasswd:
            buf = getpass.getpass("Pease input your password: ")
            buf.strip(buf)
            log.debug(buf)
        else:
            buf = pyperclip.paste()
            if buf:
                buf = buf.strip()
        return buf

    def get_master_passwd(self):
        return getpass.getpass("Please input master password: ").strip()

    def get_and_auth_master_passwd(self):
        passwd = self.get_master_passwd()
        log.debug(passwd)
        if crypto.auth(self._config['auth_info'], passwd):
            return passwd
        else:
            print("wrong password")
            return None

    def excute(self, parser):
        parser.parse_args(sys.argv[1:], namespace=self)
        log.setLevel(self.loglevel)
        log.debug(self.__dict__)
        if self.func:
            self.func(self)
        else:
            parser.print_help()

    def init(self):
        log.info("init")
        home = Path.home()
        onepasswd_dir = os.path.join(home, ".onepasswd")
        if os.path.exists(onepasswd_dir):
            log.warning("already inited, try rm -r ~/.onepasswd to re-init")
            if not self.force:
                return
        else:
            os.makedirs(onepasswd_dir)
        conf_path = os.path.join(onepasswd_dir, "onepasswd.conf")
        print("create conf {}".format(conf_path))
        db_path = os.path.join(onepasswd_dir, "db")
        if not self.backup_path:
            backup_path = os.path.join(onepasswd_dir, "backup")
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)
        self._config['db'] = db_path
        self._config['backup'] = backup_path
        passwd = self.get_master_passwd()
        self._config['auth_info'] = crypto.generate_auth_info(passwd)
        if self.user:
            self._config['user'] = self.user
        if self.token:
            if self.token == "getpass":
                self.token = getpass.getpass("please  input github token: ")
            self._config['token'] = crypto.encrypt_passwd(self.token, passwd)
        self._config['repo'] = self.repo
        if not os.path.exists(db_path):
            print("create db {}".format(db_path))
            with open(db_path, "w") as fp:
                json.dump({}, fp)

    def ask_comfirm(self, prompt):
        yn = input(prompt)
        return yn == 'y' or yn == 'Y'

    def comfirm_before_modify(self, entry):
        if self.entry in self.db:
            if not self.ask_comfirm("entry " + str(self.entry) + " already in db, want to update? (y/n)"):
                return False
            else:
                self.db.backup(self._config['backup'])
        return True

    def add(self):
        log.debug('add')
        if not self.comfirm_before_modify(self.entry):
            return
        master_passwd = self.get_and_auth_master_passwd()
        if not master_passwd:
            return
        passwd = PasswdGen.generate(self.length, self._init_passwd_gen())
        self.db[self.entry] = crypto.encrypt_passwd(passwd, master_passwd)
        self.return_password(passwd)
        print("add success")
        if self.ask_comfirm("continue to sync? (y/n)"):
            self.sync(master_passwd)

    def save(self):
        log.debug('save')
        if not self.comfirm_before_modify(self.entry):
            return
        passwd = self.get_password()
        log.debug('`' + passwd + '`')
        master_passwd = self.get_and_auth_master_passwd()
        if not master_passwd:
            return
        self.db[self.entry] = crypto.encrypt_passwd(passwd, master_passwd)

    def query_db(self, query):
        time.process_time()
        keys = self.db.getkeys()
        log.debug(keys)
        res = []

        def _match_entry(entries, q):
            for it in q:
                find_it = False
                for e in entries:
                    if it in e:
                        find_it = True
                        break
                if not find_it:
                    return False
            return True

        for x in keys:  # []
            if _match_entry(x, query):
                res.append(x)
        log.debug('query costs %f s' % time.process_time())
        return res

    def get(self):
        log.debug('get')
        res = self.query_db(self.query)
        for x in res:
            if self.ask_comfirm(self.entry_to_str(x) + " | " + " (y/n)"):
                master_passwd = self.get_and_auth_master_passwd()
                if master_passwd:
                    passwd = crypto.decrypt_passwd(self.db[x], master_passwd)
                    self.return_password(passwd)
                return

    def version(self):
        log.debug('version')
        print(onepasswd.get_version())

    @staticmethod
    def entry_to_str(entry):
        res = ''
        for x in entry:
            res += "'{}' ".format(x)
        return ' '.join(["'" + x + "'" for x in entry])

    def list(self):
        log.debug('list')
        for i, x in enumerate(self.query_db(self.query)):
            print(self.entry_to_str(x))

    def sync(self, master_passwd=None):
        log.debug('sync')
        if master_passwd is None:
            master_passwd = self.get_and_auth_master_passwd()
        token = crypto.decrypt_passwd(self._config['token'], master_passwd)
        git = GitDB(self._config['user'], token, self._config['repo'])
        root = git.get_root_dir_info()
        db_info = git.get_file_info(root, 'db')
        if git.hashfile(self._config['db']) == db_info['sha']:
            print("local db is already updated")
            return
        # print(db_info, git.hashfile(self._config['db']))
        remote_db = git.pull(db_info)
        log.debug('get remote db +++ ' + str(remote_db))
        tmp_file = os.path.join(tempfile.gettempdir(),
                                str(time.time()) + '.tmp.db')
        with open(tmp_file, "wb") as fp:
            fp.write(remote_db)
        print("> diff >>>")
        jdiff.diff(self._config['db'], tmp_file)
        print("> merge >>>")
        jmerge.merge(self._config['db'], tmp_file)
        os.remove(tmp_file)
        with open(self._config['db'], "rb") as fp:
            git.push('db', fp.read(), root)
        print("sync success")

    def _init_passwd_gen(self):
        if self.charset:
            PasswdGen.passwd_table.append(self.charset)
            self.select += self.charset[0]
        strength = set()
        for x in self.select:
            for i, t in enumerate(PasswdGen.passwd_table):
                if x in t:
                    strength.add(i)
                    break
        return strength

    def gen(self):
        log.debug('gen')
        strength = self._init_passwd_gen()
        passwd = PasswdGen.generate(self.length, strength=strength)
        self.return_password(passwd)

    def encrypt(self):
        cont = self.get_password()
        passwd = getpass.getpass("encrypt key: ")
        print(crypto.encrypt_passwd(cont, passwd))

    def decrypt(self):
        passwd = getpass.getpass("decrypt key: ")
        self.return_password(crypto.decrypt_passwd(self.enc_passwd, passwd))


def main():
    def add_passwd_spec(parser):
        parser.add_argument('-l', '--length', type=int,
                            help='the length of password, default(%d)' % Cmd.LENGTH, default=Cmd.LENGTH)
        parser.add_argument('-s', '--select', type=str, help="select char table of password. "
                            "for each character you enter, "
                            "we will look up the corresponding generation table "
                            "and add it to the generation charset", default=Cmd.SELECT)
        parser.add_argument('-c', '--charset', type=str,
                            help="password generation charset")

    parser = argparse.ArgumentParser(
        description="password management, generate, sync")
    parser.add_argument('-p', '--printpasswd', action='store_true',
                        help="password from stdio or pyperclip")
    parser.add_argument('-f', '--force', action='store_true', default=False)
    parser.add_argument('-c', '---config', type=str,
                        help="config file path", default=Config.CONF_PATH)
    parser.add_argument('-d', '--loglevel', type=str,
                        help="log level: FATAL, ERROR, WARN, WARNING, INFO, DEBUG, NOTSET")

    subparser = parser.add_subparsers()
    parser_init = subparser.add_parser('init', help="init local config file (~/.onepasswd/onepasswd.conf) "
                                                    "including db path, github user, github api token, ")
    parser_init.add_argument('-u', '--user', type=str, help="github user id")
    parser_init.add_argument('-t', '--token', type=str,
                             help="github api token (need read/write permission)."
                             "special input 'getpass' means getting token with getpass.getpass()")
    parser_init.add_argument('-r', '--repo', type=str,
                             help="onepasswd db repo", default='onepasswd-db')
    parser_init.add_argument('-p', '--passwd', type=str,
                             help="onepasswd main password")
    parser.add_argument('--backup_path', type=str,
                        help="backup path", default=None)
    parser_init.set_defaults(func=Cmd.init)

    parser_add = subparser.add_parser(
        'add', help='add one password entry (generate password automatically)')
    parser_add.add_argument(
        'entry', type=str, help='password entry', nargs='+')
    add_passwd_spec(parser_add)
    parser_add.set_defaults(func=Cmd.add)

    parser_save = subparser.add_parser('save', help="save one password entry")
    parser_save.add_argument(
        'entry', type=str, help='password entry', nargs='+')
    parser_save.set_defaults(func=Cmd.save)

    parser_get = subparser.add_parser('get', help='get password by query')
    parser_get.add_argument(
        'query', help='query of entry', nargs='*', default=[])
    parser_get.set_defaults(func=Cmd.get)

    parser_list = subparser.add_parser('list', help="list password entries")
    parser_list.add_argument(
        'query', help='query of entry', nargs='*', default=[])
    parser_list.set_defaults(func=Cmd.list)

    parser_sync = subparser.add_parser(
        'sync', help="sync local db with remote github")
    parser_sync.set_defaults(func=Cmd.sync)

    parser_encrypt = subparser.add_parser('enc', help="encrypt")
    parser_encrypt.set_defaults(func=Cmd.encrypt)
    parser_decrypt = subparser.add_parser('dec', help="decrypt")
    parser_decrypt.add_argument(
        'enc_passwd', type=str, help='password to decrypt')
    parser_decrypt.set_defaults(func=Cmd.decrypt)

    parser_gen = subparser.add_parser('gen', help="generate password")
    add_passwd_spec(parser_gen)
    parser_gen.set_defaults(func=Cmd.gen)

    parser_version = subparser.add_parser('version', help="print version")
    parser_version.set_defaults(func=Cmd.version)

    cmd = Cmd()
    cmd.excute(parser)


if __name__ == "__main__":
    main()
