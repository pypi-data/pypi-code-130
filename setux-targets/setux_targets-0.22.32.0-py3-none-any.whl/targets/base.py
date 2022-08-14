from tempfile import NamedTemporaryFile

from setux.core.target import CoreTarget
from setux.actions.transfer import Sender, Syncer
from . import logger, info, error


class BaseTarget(CoreTarget):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.context = dict()

    def __call__(self, command, **kw):
        ret, out, err = self.run(command, **kw)
        if ret != 0:
            error(f' ! {command} -> {ret} !')
            if err:
                err = '    ! ' + '\n    ! '.join(err)
                error(f'{err}')
        info('    ' + '\n    '.join(out))
        return ret

    def send(self, src, dst=None, sudo=None):
        try:
            Sender(self, src=src, dst=dst or src, sudo=sudo)()
        except Exception as x:
            error(f'send {src} -> {dst} ! {x}')
            return False
        return True

    def sync(self, src, dst=None):
        try:
            Syncer(self, src=src, dst=dst or src)()
        except Exception as x:
            error(f'sync {src} -> {dst} ! {x}')
            return False
        return True

    def fetch(self, remote, local, sudo=None, quiet=False):
        if not quiet: info(f'\tfetch {local} <- {remote}')
        if sudo and sudo != self.distro.login.name:
            return self.do_fetch_as(sudo, remote, local, quiet)
        else:
            return self.do_fetch(remote, local, quiet)

    def read(self, path, mode='rt', sudo=None, report='normal'):
        if report=='normal':
            info(f'\tread {path}')
        with NamedTemporaryFile(mode=mode) as tmp:
            self.fetch(path, tmp.name, sudo=sudo, quiet=True)
            content = tmp.read()
        return content

    def write(self, path, content, mode='wt', sudo=None, report='normal'):
        if report=='normal':
            info(f'\twrite {path}')
        dest = path[:path.rfind('/')]
        self.run(f'mkdir -p {dest}', report=report)
        with NamedTemporaryFile(mode=mode) as tmp:
            tmp.write(content)
            tmp.flush()
            if sudo:
                self.do_send_as(sudo, tmp.name, path)
            else:
                self.do_send(tmp.name, path)
        return self.read(path, mode=mode.replace('w','r'), sudo=sudo, report='quiet') == content

