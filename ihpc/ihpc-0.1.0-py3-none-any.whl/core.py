__all__ = ['Server']


import fnmatch
import functools as f
import json
import pathlib as p
import typing as t

import paramiko

from .type import Path, StdOE


class Server:

    __version__ = '0.1.0'

    Self = __qualname__

    def __init__(self, host: str, port: int, username: str, password: str) -> None:
        self._host, self._port, self._user = host, port, username
        self._trans = paramiko.Transport((host, port))
        self._trans.connect(username=username, password=password)
        self._ssh = self._sftp = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, type, exception, traceback) -> None:
        self.close()

    def __repr__(self) -> str:
        return f'<{self._user}@{self._host}({self._port})>'

    def __truediv__(self, path: Path) -> 'RemotePath':
        # Not recommended at this time, try property root and home
        return RemotePath(path, self)

    @classmethod
    def from_files(cls, *paths: Path) -> Self:
        for path in paths:
            if isinstance(path, str):
                path = p.Path(path)
            if path.exists():
                return cls.from_file(path)
        raise FileNotFoundError

    @classmethod
    def from_file(cls, path: Path) -> Self:
        if isinstance(path, str):
            path = p.Path(path)
        return getattr(cls, f'from_{path.suffix[1:]}')(path)

    @classmethod
    def from_json(cls, path: Path) -> Self:
        if isinstance(path, str):
            path = p.Path(path)
        return cls(**json.loads(path.read_text()))

    @property
    def ssh(self) -> paramiko.SSHClient:
        if self._ssh is None:
            self._ssh = paramiko.SSHClient()
            self._ssh.load_system_host_keys()
            self._ssh._transport = self._trans
        return self._ssh

    @property
    def sftp(self) -> paramiko.SFTPClient:
        if self._sftp is None:
            self._sftp = paramiko.SFTPClient.from_transport(self._trans)
        return self._sftp

    @f.cached_property
    def home(self) -> 'RemotePath':
        stdout, _ = self.run('echo $HOME')
        return RemotePath(stdout.strip().decode(), self)

    @f.cached_property
    def root(self) -> 'RemotePath':
        return RemotePath('/', self)

    def close(self) -> None:
        if self._ssh is not None:
            self._ssh.close()
        if self._sftp is not None:
            self._sftp.close()
        self._ssh = self._sftp = None

    def run(self, command: str, cwd: t.Optional[str] = None) -> StdOE:
        if cwd is not None:
            command = f'cd {p.Path(cwd).as_posix()} && {command}'
        return self._run(command)

    def _run(self, command: str) -> StdOE:
        _, stdout, stderr = self.ssh.exec_command(command)
        return stdout.read(), stderr.read()


class RemotePath:
    Self = __qualname__

    def __init__(self, path: Path, server: Server) -> None:
        self._path = p.Path(path) if isinstance(path, str) else path
        self._server = server

    def __repr__(self) -> str:
        return repr(self._server).replace('>', f':{self.as_posix()}>')

    def __str__(self) -> str:
        return self._path.__str__()

    def __lshift__(self, path: Path) -> None:
        # upload: self << path
        raise NotImplementedError

    def __rshift__(self, path: Path) -> None:
        # download: self >> path
        raise NotImplementedError

    def __eq__(self, other: Self) -> bool:
        if not isinstance(other, self.__class__):
            raise
        return self._path == other._path

    def __hash__(self) -> int:
        return self._path.__hash__()

    def __truediv__(self, path: Path) -> Self:
        return self._new(self._path/path)

    @property
    def name(self) -> str:
        return self._path.name

    @property
    def parent(self) -> Self:
        return self._new(self._path.parent)

    @property
    def parents(self) -> Self:
        return RemotePathParents(self)

    @property
    def parts(self) -> t.Tuple[str, ...]:
        return self._path.parts

    @property
    def stem(self) -> str:
        return self._path.stem

    @property
    def suffix(self) -> str:
        return self._path.suffix

    @property
    def suffixes(self) -> t.List[str]:
        return self._path.suffixes

    def absolute(self) -> Self:
        if self._path.is_absolute():
            return self
        else:
            return self._new(self._server.home/self._path)

    def as_posix(self) -> str:
        return self._path.as_posix()

    def as_uri(self) -> str:
        return self._path.as_uri()

    def chmod(self, mode: int) -> None:
        self._server.sftp.chmod(self.as_posix(), mode)

    def exists(self) -> bool:
        try:
            self.stat()
        except OSError:
            return False
        else:
            return True

    def expanduser(self) -> Self:
        # TODO: ~user
        if self._path.parts[0] == '~':
            return self._server.home / p.Path(*self._path.parts[1:])
        else:
            return self

    def glob(self, pattern: str) -> t.Iterator[Self]:
        raise NotImplementedError

    def iterdir(self, unstable: bool = False) -> t.Iterator[Self]:
        # assert self.is_dir()
        attr = 'listdir_iter' if unstable else 'listdir_attr'
        for attr in getattr(self._server.sftp, attr)(self.as_posix()):
            yield self / attr.filename

    def is_absolute(self) -> bool:
        return self._path.is_absolute()

    def is_block_device(self) -> bool:
        return p.S_ISBLK(self.stat().st_mode)

    def is_char_device(self) -> bool:
        return p.S_ISCHR(self.stat().st_mode)

    def is_dir(self) -> bool:
        return p.S_ISDIR(self.stat().st_mode)

    def is_fifo(self) -> bool:
        return p.S_ISFIFO(self.stat().st_mode)

    def is_file(self) -> bool:
        return p.S_ISREG(self.stat().st_mode)

    def is_socket(self) -> bool:
        return p.S_ISSOCK(self.stat().st_mode)

    def is_symlink(self) -> bool:
        # return p.S_ISLNK(self.stat().st_mode)
        try:
            self.resolve()
        except OSError:
            return False
        else:
            return True

    def joinpath(self, *paths: Path) -> Self:
        return self._new(self._path.joinpath(*paths))

    @f.lru_cache
    def lstat(self) -> paramiko.SFTPAttributes:
        return self._server.sftp.lstat(self.as_posix())

    def mkdir(self, mode: int = 0o777, parents: bool = False, exist_ok: bool = False) -> None:
        try:
            self._server.sftp.mkdir(self.as_posix(), mode)
        except FileNotFoundError:
            if not parents or self.parent == self:
                raise
            self.parent.mkdir(parents=True, exist_ok=True)
            self.mkdir(mode, parents=False, exist_ok=exist_ok)
        except OSError:
            if not exist_ok or not self.is_dir():
                raise

    def open(
        self,
        mode: str = 'r', bufsize: int = -1,
        encoding: t.Optional[str] = None,
        errors: t.Optional[str] = None,
        newline: t.Optional[str] = None,
    ) -> paramiko.SFTPFile:
        return self._server.sftp.open(self.as_posix(), mode, bufsize)

    def read_bytes(self) -> bytes:
        with self.open('r') as f:
            return f.read()

    def read_text(self, encoding: str = 'utf-8', errors: str = 'strict') -> str:
        return self.read_bytes().decode(encoding, errors)

    def relative_to(self, *paths: Path) -> Self:
        return self._new(self._path.relative_to(*paths))

    def rmdir(self) -> None:
        self._server.sftp.rmdir(self.as_posix())

    def rglob(self, pattern: str) -> t.Iterator[Self]:
        for path in self.walk():
            if fnmatch.fnmatch(path.name, pattern):
                yield path

    def rename(self, path: Path) -> Self:
        path = self._absolute(path)
        self._server.sftp.rename(self.as_posix(), path.as_posix())
        return self._new(path)

    def replace(self, path: Path) -> Self:
        path = self._new(self._absolute(path))
        if path.exists():
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
            else:
                raise
        self.rename(path._path)
        return path

    def resolve(self, strict: bool = False) -> Self:
        return self._new(self._server.sftp.readlink(self.as_posix()))

    def run(self, command: str) -> StdOE:
        return self._server.run(command, cwd=self.as_posix())

    @f.lru_cache
    def stat(self) -> paramiko.SFTPAttributes:
        return self._server.sftp.stat(self.as_posix())

    def symlink_to(self, path: Path) -> None:
        path = self._absolute(path)
        self._server.sftp.symlink(path.as_posix(), self.as_posix())

    def touch(self) -> None:
        if self.exists():
            self._server.sftp.utime(self.as_posix(), None)
        else:
            self.open('w').close()

    def unlink(self) -> None:
        self._server.sftp.unlink(self.as_posix())

    def walk(self) -> t.Iterator[Self]:
        for path in self.iterdir():
            if path.is_dir():
                yield from path.walk()
            else:
                yield path

    def with_name(self, name: str) -> Self:
        return self._new(self._path.with_name(name))

    def with_suffix(self, suffix: str) -> Self:
        return self._new(self._path.with_suffix(suffix))

    def write_bytes(self, data: bytes) -> int:
        with self.open('w') as f:
            f.write(data)
        return len(data)

    def write_text(self, data: str, encoding: str = 'utf-8', errors: str = 'strict') -> int:
        with self.open('w') as f:
            f.write(data.encode(encoding, errors))
        return len(data)

    def _absolute(self, path: Path) -> p.Path:
        # assert self.is_absolute()
        if isinstance(path, str):
            path = p.Path(path)
        if not path.is_absolute():
            path = self._path.parent / path
        return path

    def _is(self) -> t.Dict[str, bool]:
        flags = {}
        for attr in dir(self):
            if attr.startswith('is_'):
                try:
                    flag = getattr(self, attr)()
                except Exception as e:
                    print(f'[{attr}] {e}')
                else:
                    if isinstance(flag, bool):
                        flags[attr] = flag
                    else:
                        print(f'[{attr}] {flag}')
        return flags

    def _new(self, path: Path) -> Self:
        return self.__class__(path, self._server)


class RemotePathParents:
    def __init__(self, path: RemotePath) -> None:
        self._path = path

    def __getitem__(self, idx: int) -> RemotePath:
        return self._path._new(self._path._path.parents[idx])
