#!/usr/bin/python3

import json
import random
import time
import os
import requests
import base64
import socket
from onepasswd import ltlog
from hashlib import sha256, sha1

log = ltlog.getLogger('onepasswd.onepasswd')

g_req_kwarg = {
    # 'verify': False
}


class GitDB(object):
    _git_server = 'https://api.github.com'

    def __init__(self, user, token, repo):
        super().__init__()
        self.user = user
        self.token = token
        self.repo = repo
        self.git_repo_api = GitDB._git_server + \
            '/repos/{user:}/{repo:}/git'.format(**self.__dict__)
        log.debug('git_repo_api ' + self.git_repo_api)

    def _add_header(self, req, header, value):
        if 'headers' in req:
            req['headers'][header] = value
        else:
            req['headers'] = {header: value}
        return req

    def _accept_json(self, req):
        return self._add_header(req, 'Accept', 'application/vnd.github.v3+json')

    def req_get_with_auth(self, *args, **kwargs):
        kwargs['auth'] = requests.auth.HTTPBasicAuth(self.user, self.token)
        kwargs.update(g_req_kwarg)
        resp = requests.get(*args, **kwargs)
        log.debug(resp)
        return resp

    def req_post_with_auth(self, *args, **kwargs):
        kwargs['auth'] = requests.auth.HTTPBasicAuth(self.user, self.token)
        kwargs.update(g_req_kwarg)
        resp = requests.post(*args, **kwargs)
        log.debug(resp)
        return resp

    def req_patch_with_auth(self, *args, **kwargs):
        kwargs['auth'] = requests.auth.HTTPBasicAuth(self.user, self.token)
        kwargs.update(g_req_kwarg)
        resp = requests.patch(*args, **kwargs)
        log.debug(resp)
        return resp

    def _get_master(self):
        resp = self.req_get_with_auth(self.git_repo_api + '/refs/heads/master',
                                      **self._accept_json({}))
        if resp.status_code == 200:
            log.debug(resp.content)
            log.debug(resp.json())
            return resp.json()
        else:
            return {}

    def _update_master(self, commit):
        resp = self.req_patch_with_auth(
            self.git_repo_api + '/refs/heads/master', json={'sha': commit})
        return resp.json()

    def _get_commit(self, _sha):
        resp = self.req_get_with_auth(self.git_repo_api + '/commits/{sha:}'.format(sha=_sha),
                                      **self._accept_json({}))
        if resp.status_code == 200:
            log.debug(resp.json())
            return resp.json()
        else:
            return {}

    def _create_commit(self, tree, msg, parents=[]):
        resp = self.req_post_with_auth(self.git_repo_api + '/commits', json={
            'parents': parents,
            'tree': tree,
            'message': msg
        })
        if resp.status_code == 201:
            return resp.json()
        else:
            return {}

    def _get_tree(self, _sha):
        resp = self.req_get_with_auth(self.git_repo_api + '/trees/{sha:}'.format(sha=_sha),
                                      **self._accept_json({}))
        if resp.status_code == 200:
            log.debug(resp.json())
            return resp.json()
        else:
            return {}

    def _create_tree(self, tree):
        """
        [{
            'path': blob['name'],
            "mode": "100644",
            "type": "blob",
            "sha": blob['sha'],
        }, ]
        """
        resp = self.req_post_with_auth(self.git_repo_api + '/trees', json={
            "tree": tree
        })
        if resp.status_code == 201:
            return resp.json()
        else:
            log.warn(resp.json())
            return {}

    def _get_blob(self, _sha):
        resp = self.req_get_with_auth(self.git_repo_api + '/blobs/{sha:}'.format(sha=_sha),
                                      **self._accept_json({}))
        if resp.status_code == 200:
            log.debug(resp.json())
            return resp.json()
        else:
            return {}

    def _create_blob(self, cont):
        resp = self.req_post_with_auth(self.git_repo_api + '/blobs', json={
            'encoding': 'base64',
            'content': base64.b64encode(cont).decode()
        })
        return resp.json()

    def _match_in_list(self, _list, key, val):
        for x in _list:
            if x[key] == val:
                return x
        return {}

    def decode_blob(self, cont):
        if cont['encoding'] == 'base64':
            log.debug('decode {:d} byte with base64'.format(cont['size']))
            return base64.b64decode(cont['content'].encode())
        else:
            return None

    def _gen_commit_msg(self):
        localname = socket.gethostname()
        create_time = time.ctime()
        return "[{time:}] @ {name}".format(time=create_time, name=localname)

    def get_root_dir_info(self):
        ref = self._get_master()
        log.debug(ref['object']['sha'])
        com = self._get_commit(ref['object']['sha'])
        tree = self._get_tree(com['tree']['sha'])
        tree['commit'] = com['sha']
        log.debug(tree)
        return tree

    def get_file_info(self, parent_dir_info, file_name):
        file_info = self._match_in_list(
            parent_dir_info['tree'], 'path', file_name)
        log.debug(file_info)
        return file_info

    def pull(self, file_info):
        resp = self._get_blob(file_info['sha'])
        if resp:
            return self.decode_blob(resp)
        else:
            return {}

    def _filter_dict(self, d, keys):
        log.debug(str(keys) + ' ' + str(d))
        return {key: d[key] for key in keys}

    def push(self, file_name, content, parent_dir_info):
        # parent_dir_info
        tmp = self._match_in_list(parent_dir_info['tree'], 'path', file_name)
        if tmp:
            parent_dir_info['tree'].remove(tmp)
        resp = self._create_blob(content)
        parent_dir_info['tree'].append({
            'path': file_name,
            "mode": "100644",
            "type": "blob",
            "sha": resp['sha']
        })
        resp = self._create_tree(list(
            map(lambda x: self._filter_dict(x, ['path', "mode", "type", "sha"]), parent_dir_info['tree'])))
        log.debug(resp)
        resp = self._create_commit(resp['sha'], self._gen_commit_msg(), [
                                   parent_dir_info['commit']])
        resp = self._update_master(resp['sha'])
        log.debug(resp)
        return resp

    def hashfile(self, file):
        res = None
        with open(file, "rb") as fp:
            length = fp.seek(0, os.SEEK_END)
            fp.seek(0, os.SEEK_SET)
            header = b'blob ' + str(length).encode() + b'\x00'
            res = sha1(header + fp.read()).hexdigest().lower()
        return res


class PasswdGen(object):
    passwd_table = ["abcdefghijklmnopqrstuvwxyz",
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                    "0123456789",
                    "@_-~,.#$"]

    @staticmethod
    def check_strength(passwd, strength):
        vis = set()
        for x in passwd:
            for i, t in enumerate(PasswdGen.passwd_table):
                if x in t:
                    vis.add(i)
        if vis != strength:
            return False
        return True

    @staticmethod
    def generate(length=12, strength=set(range(0, len(passwd_table)))):
        table = ''.join([PasswdGen.passwd_table[i] for i in strength])
        passwd = ''
        for i in range(length):
            passwd += random.choice(table)

        if PasswdGen.check_strength(passwd, strength):
            return passwd
        else:
            return PasswdGen.generate(length, strength)


class DB(dict):
    def __init__(self, path, default={}):
        self.path = path
        self.db = default
        self._load_from_disk()

    def __getitem__(self, entries):
        key = DB.cal_key(entries)
        return self.db[key]['passwd']

    @staticmethod
    def cal_key(entries):
        return sha256(json.dumps(entries).replace('\n', '').replace('\t', '').encode('utf-8')).hexdigest()

    def __setitem__(self, entries, val):
        key = DB.cal_key(entries)
        if key in self.db and self.db[key]['passwd'] == val:
            return
        self.db[key] = {'entries': entries,
                        'passwd': val, 'time': str(time.time())}
        self._write_to_disk()

    def __delitem__(self, entries):
        key = DB.cal_key(entries)
        if key not in self.db:
            return
        self.db.__delitem__(key)
        self._write_to_disk()

    def __contains__(self, entries):
        return self.db.__contains__(DB.cal_key(entries))

    def _write_to_disk(self, path=None):
        path = path if path else self.path
        with open(path, 'w') as fp:
            json.dump(self.db, fp, indent=2)

    def _load_from_disk(self, path=None, default={}):
        path = path if path else self.path
        if not os.path.exists(path):
            self._write_to_disk(path)
        with open(path) as fp:
            self.db = json.load(fp)

    def backup(self, backup_path):
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)
        bck_file = os.path.join(backup_path, str(time.time()) + '.db')
        self._write_to_disk(bck_file)

    def rollback(self, timestamp, backup_path):
        timestamp = str(timestamp)
        bck_file = os.path.join(backup_path, timestamp + '.db')
        if not os.path.exists(bck_file):
            print("[Abort] '{}' not found".format(bck_file))
            return
        # do backup
        self.backup()
        self._load_from_disk(bck_file)

    def getkeys(self):
        return [x['entries'] for k, x in self.db.items()]
