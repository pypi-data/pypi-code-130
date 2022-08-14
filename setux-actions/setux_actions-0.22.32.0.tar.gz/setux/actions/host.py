from setux.core.action import Actions, Action


class hostanme(Action):
    @property
    def label(self):
        return 'hostname'

    def check(self):
        ret, out, err = self.target.run('hostname')
        return out[0] == self.hostname

    def deploy(self):
        ret, out, err = self.target.run(f'hostname {self.hostname}', sudo='root')
        if ret: raise RuntimeError('!! ' + err[0])
        return ret == 0


class etc_hostanme(Action):
    @property
    def label(self):
        return '/etc/hostname'

    def check(self):
        current = self.target.read('/etc/hostname').strip()
        return current == self.hostname

    def deploy(self):
        ok = self.target.write(
            '/etc/hostname',
            f'{self.hostname}\n',
            sudo = 'root',
        )
        return ok


class etc_hosts(Action):
    @property
    def label(self):
        return '/etc/hosts'

    def check(self):
        current = self.target.read('/etc/hosts')
        return self.hostname in current

    def deploy(self):
        current = self.target.read('/etc/hostname').strip()
        new_hosts = self.target.read('/etc/hosts')
        new_hosts = new_hosts.replace(current, self.hostname)
        ok = self.target.write(
            '/etc/hosts',
            new_hosts,
            sudo = 'root',
        )
        return ok


class Hostname(Actions):
    @property
    def label(self):
        return f'hostname {self.hostname}'

    @property
    def actions(self):
        return [
            etc_hosts,
            etc_hostanme,
            hostanme,
        ]

