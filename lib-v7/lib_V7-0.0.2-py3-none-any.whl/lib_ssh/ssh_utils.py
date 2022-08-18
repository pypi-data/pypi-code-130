import os
import paramiko
import lib_ssh.ssh_base_api as ssh_base_api

def acquire_client( **auth_args ):
    if 'pkey' in auth_args:
        auth_args['pkey'] = paramiko.RSAKey.from_private_key_file(auth_args['pkey'])
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(**auth_args)
    return client


def standard_client( target_server_ip, key_path ):
    key = paramiko.RSAKey.from_private_key_file(key_path)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=target_server_ip, username="ubuntu", pkey=key)
    return client


def scp_file( target_server_ip, key_path, source_path, remote_server_path, user ):
    scp_cmd = f'sudo scp -i {key_path} {source_path} {user}@{target_server_ip}:{remote_server_path}'
    os.system(scp_cmd)


def scp_dir( target_server_ip, key_path, source_path, remote_server_path, user ):
    scp_cmd = f'sudo scp -i {key_path} -r {source_path} {user}@{target_server_ip}:{remote_server_path}'
    os.system(scp_cmd)


def run_cmd( client, cmd_repr, root_pw='' ):
    result = ssh_base_api.run_cmd_client( client, cmd_repr, root_pw )
    return result


def run_cmd_L1( client, cmd_repr_L1, root_pw='' ):
    result = [
            ssh_base_api.run_cmd_client( client, cmd_repr_L1[i], root_pw )
            for i in range(0, len(cmd_repr_L1))
        ]
    return result


def write_file( client, remote_server_path, file_repr, mode, root_pw='', writeable_path='' ):
    ftp = client.open_sftp()
    result = ssh_base_api.write_ftp( client, ftp, remote_server_path, file_repr, mode, root_pw, writeable_path )
    ftp.close()
    return result


def read_file( client, remote_server_path, mode, root_pw='' ):
    ftp = client.open_sftp()
    result = ssh_base_api.read_ftp( client, ftp, remote_server_path, mode, root_pw )
    ftp.close()
    return result


def write_file_L1( client, remote_server_path_L1, file_repr_L1, mode_L1, root_pw='', writeable_path='' ):
    ftp = client.open_sftp()
    result = [
            ssh_base_api.write_ftp( client, ftp, remote_server_path_L1[i], file_repr_L1[i], mode_L1[i], root_pw, writeable_path )
            for i in range(0, len(remote_server_path_L1))
        ]
    ftp.close()
    return result


def read_file_L1( client, remote_server_path_L1, mode_L1, root_pw='' ):
    ftp = client.open_sftp()
    result = [
            ssh_base_api.read_ftp( client, ftp, remote_server_path_L1[i], mode_L1[i], root_pw )
            for i in range(0, len(remote_server_path_L1))
        ]
    ftp.close()
    return result


def mkdir( client, remote_server_path, root_pw='' ):
    cmd_repr = f'mkdir {remote_server_path}'
    result = ssh_base_api.run_cmd_client( client, cmd_repr, root_pw )
    return result


def mkdir_L1( client, remote_server_path_L1, root_pw='' ):
    cmd_repr_L1 = [
            f'mkdir {remote_server_path_L1[i]}'
            for i in range(0, len(remote_server_path_L1))
        ]
    result = [
            ssh_base_api.run_cmd_client( client, cmd_repr_L1[i], root_pw )
            for i in range(0, len(remote_server_path_L1))
        ]
    return result


def service_ctl(client, service_prefix, root_pw, ctl_op):
    if ctl_op not in ['start', 'stop', 'restart', 'status']:
        return ['invalid op', '']
    cmd_repr = f'service {service_prefix}_server {ctl_op}'
    if ctl_op in ['start', 'stop', 'restart']:
        out, err = run_cmd( client, cmd_repr, root_pw=root_pw )
        return [ x for x in [out, err] ]
    out, err = run_cmd( client, cmd_repr, root_pw=root_pw )
    out1 = out
    i1 = out1.find('Active', 0)
    i2 = out1.find('\n', i1+1)
    interpreted_result = out1[i1:i2]
    return [ x for x in [err] ] + [ interpreted_result ]


def list_services(client, root_pw=''):
    cmd_repr = 'systemctl list-units --state=running'
    return run_cmd( client, cmd_repr, root_pw=root_pw )


def write_systemctl_repr( client, service_name, service_def_repr, root_pw='', writeable_path='' ):
    remote_server_path = f'/etc/systemd/system/{service_name}.service'
    mode = 'w'
    return write_file( client, remote_server_path, service_def_repr, mode, root_pw=root_pw, writeable_path=writeable_path )
