from pybrary.ascii import clean_name

from setux.logger import silent
from setux.core.action import Action


class Downloader(Action):
    @property
    def label(self):
        return f'<- {self.name}'

    def check(self):
        dest = self.target.file.fetch(self.dest, sudo=self.sudo)
        return dest.size and dest.size > 0

    def deploy(self):
        if self.sudo:
            bak = self.dest
            self.target.dir('/tmp/setux/dload', mode=777, sudo=self.sudo, verbose=False)
            self.dest = f'/tmp/setux/dload/{clean_name(self.name)}'

        ok = self.target.download(
            url = self.url,
            dst = self.dest,
        )

        if self.sudo:
            ret, out, err = self.target.run(f'cp {self.dest} {bak}', sudo=self.sudo, report='quiet')
            ok = ok and ret==0
            self.dest = bak

        self.target.file(self.dest, verbose=False,
            user  = self.user,
            group = self.group,
            mode  = self.mode,
            sudo  = self.sudo,
        )

        return ok


class Sender(Action):
    @property
    def labeler(self):
        return silent

    @property
    def label(self):
        dst = f' -> {self.dst}' if self.dst != self.src else ''
        return f'send {self.src}{dst}'

    def check(self):
        lhash = self.local.file(self.src, verbose=False).hash
        rhash = self.target.file(self.dst, verbose=False).hash
        return rhash == lhash

    def deploy(self):
        if hasattr(self, 'sudo') and self.sudo:
            return self.target.do_send_as(self.sudo, self.src, self.dst)
        else:
            return self.target.do_send(self.src, self.dst)


class Syncer(Action):
    @property
    def label(self):
        dst = self.dst if hasattr(self, 'dst') else self.src
        dst = f' -> {dst}' if dst != self.src else ''
        return f'sync {self.src}{dst}'

    def check(self):
        dst = self.dst if hasattr(self, 'dst') else self.src
        lhash = self.local.dir(self.src, verbose=False).hash
        rhash = self.target.dir(dst, verbose=False).hash
        return rhash == lhash

    def deploy(self):
        dst = self.dst if hasattr(self, 'dst') else self.src
        return self.target.do_sync(self.src, dst)
