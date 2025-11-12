import os
import sys
from datetime import datetime

from fabric import Connection
from invoke.exceptions import UnexpectedExit, AuthFailure


class Host:
    def __init__(self,
                 hostname: str = None,
                 ip: str = None,
                 port: int = 22,
                 user: str = "root",
                 password: str = "",
                 identity: str = None
                 ):
        self.hostname = hostname
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.identity = identity

        if hostname is None and ip is None:
            raise ValueError("Neither hostname nor ip address provided")

        ckw = {
            "password": self.password
        }
        if self.identity:
            ckw["key_filename"] = self.identity

        self.conn = Connection(
            host=self.hostname if self.hostname else self.ip,
            port=self.port,
            user=self.user,
            connect_kwargs=ckw
        )

    def run(self, cmd, **kwargs):
        return self.conn.run(command=cmd, **kwargs)

    def download(self, file, dest=None):
        self.conn.get(file, local=dest)

    def upload(self, file, dest):
        self.conn.put(file, remote=dest)



def test_connection(host):
    try:
        host.conn.run('echo "SSH connection successful"')
        return True
    except FileNotFoundError as e:
        print(
            f"SSH connection failed. Private key file not found {host.identity}")
        return False
    except TimeoutError as e:
        print(f"SSH connection timed out. {e}")
        return False
    except (UnexpectedExit, AuthFailure, Exception) as e:
        print(f"SSH connection failed: {type(e)}-{e}")
        return False


def ssh(host, comm, **kwargs):
    return host.run(comm, **kwargs)


def touch(file_path):
    """
    Checks if the file at `file_path` exists. If not, creates the file and any necessary subfolders.
    """
    # Extract the directory from the file path
    directory = os.path.dirname(file_path)

    # Create the directory if it doesn't exist
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # Create the file if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            pass  # Creates an empty file

    # Example usage:
    # touch("data/output/results.txt")


def touch_remote(host, path, hide=True):
    remote_mkdir(host, os.path.dirname(path), hide=hide)
    host.run(f"touch {path}", hide=hide)


def remote_mkdir(host, path, hide=True):
    host.run(f"mkdir -p {path}", hide=hide)


def remote_is_dir(host, path, hide=True):
    if remote_path_exists(host, path):
        test = host.run(f"test -d {path} && echo 0 || echo 1", hide=hide).stdout
        return test.strip() == "0"
    else:
        raise FileNotFoundError(f"Error. Dir {host.hostname}:{path} does not exist")


def remote_file_info(host, path, hide=True):
    try:
        data = host.run(f'stat -c "%s %Y" "{path}"', hide=hide).stdout
    except UnexpectedExit as e:
        print(f"Error getting remote file info. "
              f"File {host.hostname}:{path} does not exist",
              file=sys.stderr)
        # print(e)
        return None

    size_str, timestamp_str = data.split()
    size_bytes = int(size_str)
    last_modified = datetime.fromtimestamp(int(timestamp_str))

    return {
        "path": path,
        "size_bytes": size_bytes,
        "last_modified": last_modified
    }


def remote_dir_info(host, path, hide=True):
    try:
        dir_size = host.run(f"du -sb {path}", hide=hide).stdout.split("\t")[0]
        lm_ts = host.run(f'stat -c "%Y" "{path}"', hide=hide).stdout
        last_modified= datetime.fromtimestamp(int(lm_ts))
    except UnexpectedExit as e:
        print(f"Error getting remote dir info. "
              f"Directory {host.hostname}:{path} does not exist",
              file=sys.stderr)
        # print(e)
    return {
        "path": path,
        "size_bytes": int(dir_size),
        "last_modified": last_modified
    }



def remote_file_exists(host, path, hide=True):
    tst = host.run(f"test -f {path} && echo 0 || echo 1",
                   hide=hide).stdout.strip()
    return tst == "0"


def remote_dir_exists(host, path, hide=True):
    tst = host.run(f"test -d {path} && echo 0 || echo 1",
                   hide=hide).stdout.strip()
    return tst == "0"

def remote_path_exists(host, path, hide=True):
    tst = host.run(f"test -e {path} && echo 0 || echo 1", hide=hide).stdout.strip()
    return tst == "0"

def rename_remote_file(host, file, new_name, hide=True):
    if remote_path_exists(host, file, hide=hide):
        dirname = os.path.dirname(file)
        new_path = f"{dirname}/{new_name}"
        host.run(f"mv {file} {new_path}", hide=hide)
    else:
        raise FileNotFoundError(f"Error renaming remote file. \n"
                                f"File {host.hostname}:{file} does not exist!")


def rename_remote_dir(host, rdir, new_name, hide=True):
    if remote_path_exists(host,rdir,hide=hide):
        new_path = rdir.split('/')[:-2] + [new_name]
        new_path = "/".join(new_path)
        host.run(f"mv {rdir} {new_path}",hide=True)
    else:
        raise FileNotFoundError(f"Error renaming remote directory. \n"
                                f"Directory {host.hostname}:{rdir} does not exist!")


def move_remote_file(host, src, dest, hide=True):
    if remote_file_exists(host,src, hide=hide):
        if remote_file_exists(host,dest, hide=True):
           raise FileExistsError(f"Error moving remote file. \n"
                                 f"Destination file {host.hostname}:{dest} already exists")
        touch_remote(host,dest, hide=hide) #make sure file and dirs exits
        host.run(f"mv {src} {dest}",hide=hide)
    else:
        raise FileNotFoundError(f"Error moving remote file. \n"
                                f"File {host.hostname}:{src} does not exist!")


def move_remote_dir(host, src, dest, hide=True):
    if remote_dir_exists(host, src, hide=hide):
        if remote_dir_exists(host, dest, hide=hide):
            raise FileExistsError(f"Error moving remote directory. \n"
                                  f"Destination directory {host.hostname}:{dest} already exists")
        remote_mkdir(host, dest, hide=hide)  # make sure file and dirs exits
        host.run(f"mv {src} {dest}", hide=hide)
    else:
        raise FileNotFoundError(f"Error moving remote file. \n"
                                f"File {host.hostname}:{src} does not exist!")


def copy_remote_file(host, src, dest, hide=True):
    if remote_file_exists(host, src, hide=hide):
        if remote_file_exists(host,dest, hide=True):
           raise FileExistsError(f"Error copying remote file. \n"
                                 f"Destination file {host.hostname}:{dest} already exists")
        touch_remote(host, dest, hide=hide)  # make sure file and dirs exits
        host.run(f"cp {src} {dest}", hide=hide)
    else:
        raise FileNotFoundError(f"Error cp remote file. \n"
                                f"File {host.hostname}:{src} does not exist!")


def copy_remote_dir(host, src, dest, hide=True):
    if remote_dir_exists(host, src, hide=hide):
        if remote_dir_exists(host, dest, hide=hide):
            raise FileExistsError(f"Error copying remote directory. \n"
                                  f"Destination directory {host.hostname}:{dest} already exists")
        remote_mkdir(host, dest, hide=hide)  # make sure file and dirs exits
        host.run(f"cp {src} {dest}", hide=hide)
    else:
        raise FileNotFoundError(f"Error moving remote file. \n"
                                f"File {host.hostname}:{src} does not exist!")


def download_file(host, rem_file, dest=None):
    if not dest is None:
        if os.path.isdir(dest):
            fname = os.path.basename(rem_file)
            dest=os.path.join(dest,fname)
    host.download(rem_file,dest=dest)


def download_dir(host, rem_path, dest_path=None):
    if dest_path is None:
        dirname = os.path.basename(os.path.normpath(rem_path))
        dest_path = os.path.join(os.getcwd(),dirname)
    # Step 1: Get all directories and create them locally
    dir_result = host.run(f"find {rem_path} -type d", hide=True)
    remote_dirs = dir_result.stdout.strip().split('\n')

    for remote_subdir in remote_dirs:
        relative_path = os.path.relpath(remote_subdir, rem_path)
        local_subdir = os.path.join(dest_path, relative_path)
        os.makedirs(local_subdir, exist_ok=True)
        #print(f"Created local directory: {local_subdir}")

    # Step 2: Get all files and download them
    file_result = host.run(f"find {rem_path} -type f", hide=True)
    remote_files = file_result.stdout.strip().split('\n')

    for remote_file in remote_files:
        relative_path = os.path.relpath(remote_file, rem_path)
        local_file_path = os.path.join(dest_path, relative_path)
        host.download(remote_file, dest=local_file_path)
        #print(f"Downloaded: {remote_file} → {local_file_path}")


def delete_remote_file(host, path):
    try:
        host.run(f"rm {path}")
    except UnexpectedExit as e:
        print(f"Error deleting remote file. "
              f"File {host.hostname}:{path} does not exist",
              file=sys.stderr)


def delete_remote_dir(host, path):
    try:
        host.run(f"rm -rf {path}")
    except UnexpectedExit as e:
        print(f"Error deleting remote directory."
              f"Directory {host.hostname}:{path} does not exist",
              file=sys.stderr)


def truncate_remote_file(host, path):
    try:
        host.run(f"truncate --size 0 {path}")
    except UnexpectedExit as e:
        print(f"Error truncating remote file."
              f"File {host.hostname}:{path} does not exist",
              file=sys.stderr)


def delete_remote_dir_content(host, path):
    try:
        host.run(f"rm -rf {path}/*")
    except UnexpectedExit as e:
        print(f"Error deleting remote directory content."
              f"Directory {host.hostname}:{path} does not exist",
              file=sys.stderr)


def upload_file(host, file, rem_dest):
    host.upload(file, rem_dest)


def upload_dir(host, local_dir, dest_dir):
    # TODO
    pass


def zip_remote_dir(host, dir_path):
    tar_fname = os.path.basename(os.path.normpath(dir_path)) + ".tar"
    tar_dir = "/".join(dir_path.split("/")[:-1])
    tar_path = "/".join([tar_dir, tar_fname])
    host.run(f"tar -a -cf {tar_path} -C {dir_path} .")
    return tar_path


def zip_and_download(host, remote_dir, dest=None):
    if dest is None:
        dest = os.getcwd()
    archive = zip_remote_dir(host, remote_dir)
    download_file(host,archive,dest)