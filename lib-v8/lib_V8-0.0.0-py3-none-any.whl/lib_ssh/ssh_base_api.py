import os
import paramiko

def run_cmd_client( client, cmd_repr, root_pw ):
    cmd_repr_exe = cmd_repr
    if len(root_pw) > 0:
        cmd_repr_exe = f'echo \"{root_pw}\" | sudo -S {cmd_repr}'
    stdin, stdout, stderr = client.exec_command( cmd_repr_exe )
    return [ x.decode() for x in  [ stdout.read(), stderr.read() ] ]


def write_ftp( client, ftp, remote_server_path, file_repr, mode, root_pw, writeable_path ):
    if len(root_pw) == 0:
        fp = ftp.file(remote_server_path, mode, -1)
        result = fp.write(file_repr)
        fp.flush()
        fp.close()
        return result
    fp = ftp.file(writeable_path, mode, -1)
    writeable_result = fp.write(file_repr)
    fp.flush()
    fp.close()
    mv_cmd = f'mv {writeable_path} {remote_server_path}'
    mv_op = run_cmd_client( client, mv_cmd, root_pw )
    return [ writeable_result, mv_op ]


def read_ftp( client, ftp, remote_server_path, mode, root_pw ):
    cmd_repr = f'cat {remote_server_path}'
    cmd_repr_exe = cmd_repr
    if len(root_pw) > 0:
        cmd_repr_exe = f'echo \"{root_pw}\" | sudo -S {cmd_repr}'
    stdin, stdout, stderr = client.exec_command( cmd_repr_exe )
    return [ stdout.read(), stderr.read() ]
