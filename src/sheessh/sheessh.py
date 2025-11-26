import os
import sys
import json
from pathlib import Path, PureWindowsPath
from datetime import datetime

from fabric import Connection
from invoke.exceptions import UnexpectedExit, AuthFailure
from paramiko.ssh_exception import BadAuthenticationType

"""
This module provides functions for manipulating remote file systems via ssh and SFTP
The motivation behind this module was to ease up downloading and truncating GSS logs
in order to be able efficiently capture data for R&D in application tests.   
Author: David Rejchrt (david.rejchrt@leica-geosystems.com) 
"""


class Host:
    """
    This class collects the connection parameters like hostname, ip address, authentication etc.
    """

    def __init__(self,
                 hostname: str = None,
                 ip: str = None,
                 port: int = 22,
                 user: str = "root",
                 password: str = "",
                 identity: str = None
                 ):
        """
        Constructor for Host. Either hostname (e.g. TS20-4790086) or IP address must be provided.
        Otherwise, a ValueError is raised.

        If key based authentication is required, the identity file has to be provided via the identity
        parameter.

        :param hostname: hostname
        :param ip: IP Address (Dot-decimal notation)
        :param port: port number. Default is 22.
        :param user: username. Default is "root"
        :param password: password. Default is empty string.
        :param identity: path to identity file, if
        """
        self.hostname = hostname
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.identity = identity

        # If neither are provided, connection impossible
        if hostname is None and ip is None:
            raise ValueError("Neither hostname nor ip address provided")

        ckw = {  # ckw = Connection Key Words
            "password": self.password
        }
        if self.identity:
            ckw["key_filename"] = self.identity

        # Connection from the "fabric" package.
        self.conn = Connection(
            host=self.ip if self.ip else self.hostname,
            port=self.port,
            user=self.user,
            connect_kwargs=ckw
        )

    def run(self, cmd: str, **kwargs):
        """
        This function executes a command on the remote machine and captures the outputs
        It is a wrapper for the fabric connection run method.

        Uses the hide kwarg to control whether the remote command output will be printed or not.

        :param cmd: command to be run on the remote machine
        :param kwargs:
        :return:
        """
        return self.conn.run(command=cmd, **kwargs)

    def download(self, file, dest=None):
        """
        Download a remote file to specified destination on local system.
        Regarding creating directories etc; the behaviour is consistent with the behaviour
        of scp or sftp commands.

        Wrapper for the fabric transfer get method.
        https://docs.fabfile.org/en/latest/api/transfer.html#fabric.transfer.Transfer.get

        :param file: path to a file on the remote system
        :param dest: local path
        :return:
        """
        self.conn.get(file, local=dest)

    def upload(self, file, dest):
        """
        Uploads local file to specified remote destination.
        Regarding creating directories etc; the behaviour is consistent with the behaviour
        of scp or sftp commands.https://docs.fabfile.org/en/latest/api/transfer.html#fabric.transfer.Transfer.put


        Wrapper for the fabric transfer put method.

        :param file: path to a file on the remote system
        :param dest: local path
        :return:
        """

        self.conn.put(file, remote=dest)


def test_connection(host: Host):
    """
    Tests whether connection can be established. If not, provides reason.
    :param host:
    :return:
    """
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
    except (AuthFailure, BadAuthenticationType) as e:
        print("Authentication failed: Check username, password and or correctness of identity file")
        print(e)
    except (UnexpectedExit, Exception) as e:
        print(f"SSH connection failed: {type(e)}-{e}")
        return False


def ssh(host: Host, comm: str, **kwargs):
    """
    Runs a command on specified host.
    :param host:
    :param comm:
    :param kwargs:
    :return:
    """
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


def touch_remote(host: Host, path, hide: bool = True):
    """
    Checks if the file at `path` on remote host exists. If not, creates the file and any necessary subdirs.

    :param host: target host
    :param path: remote path
    :param hide: controls whether the output will be printed to stdout
    :return:
    """
    remote_mkdir(host, os.path.dirname(path), hide=hide)
    host.run(f"touch {path}", hide=hide)


def remote_mkdir(host: Host, path, hide: bool = True):
    """
    Creates a directory on remote the remote host at specified path.
    Creates necessary subfolders
    :param host:  target host
    :param path: path to the new remote directory
    :param hide: controls whether the output will be printed to stdout
    :return:
    """
    host.run(f"mkdir -p {path}", hide=hide)


def remote_is_dir(host: Host, path, hide: bool = True) -> bool:
    """
    Checks, whether path on remote host is a directory or not.
    If the path does not exist, FileNotFoundError is raised.
    :param host: target host
    :param path: target path
    :param hide: controls whether the output will be printed to stdout
    :return: bool
    """
    if remote_path_exists(host, path):
        test = host.run(f"test -d {path} && echo 0 || echo 1", hide=hide).stdout
        return test.strip() == "0"
    else:
        raise FileNotFoundError(f"Error. Dir {host.hostname}:{path} does not exist")


def remote_file_info(host: Host, path, hide: bool = True):
    """
    Gets size and last modified time of a file on remote host.
    If the file does not exist or is a directory, FileNotFoundError is raised.
    :param host: target host
    :param path: path to the remote file
    :param hide:  controls whether the output will be printed to stdout
    :return: dictionary containing the path, file size in bytes and last modified date ad datetime
    """

    if remote_path_exists(host, path, hide=hide):
        if not remote_is_dir(host, path, hide=hide):
            data = host.run(f'stat -c "%s %Y" "{path}"', hide=hide).stdout
        else:
            raise FileNotFoundError(f"Error. Path {host.hostname}:{path} is not a file")
    else:
        raise FileNotFoundError(f"Error. File {host.hostname}:{path} does not exist")

    # try:
    #     data = host.run(f'stat -c "%s %Y" "{path}"', hide=hide).stdout
    # except UnexpectedExit as e:
    #     print(f"Error getting remote file info. "
    #           f"File {host.hostname}:{path} does not exist",
    #           file=sys.stderr)
    #     return None

    # Neatly format data from strings to appropriate data types
    size_str, timestamp_str = data.split()
    size_bytes = int(size_str)
    last_modified = datetime.fromtimestamp(int(timestamp_str))

    return {
        "path": path,
        "size_bytes": size_bytes,
        "last_modified": last_modified
    }


def remote_dir_info(host, path, hide: bool = True):
    """
        Gets the size and last modified time of a directory on remote host.
        If the direcotry does not exist or is a file, FileNotFoundError is raised.
        :param host: target host
        :param path: path to the remote file
        :param hide:  controls whether the output will be printed to stdout
        :return: dictionary containing the path, directory size in bytes and last modified date ad datetime
        """
    if remote_path_exists(host, path):
        if remote_is_dir(host, path, hide=hide):
            dir_size = host.run(f"du -sb {path}", hide=hide).stdout.split("\t")[0]
            lm_ts = host.run(f'stat -c "%Y" "{path}"', hide=hide).stdout
            last_modified = datetime.fromtimestamp(int(lm_ts))
            return {
                "path": path,
                "size_bytes": int(dir_size),
                "last_modified": last_modified
            }
        else:
            raise FileNotFoundError(f"Error. Path {host.hostname}:{path} is not a directory")
    else:
        raise FileNotFoundError(f"Error. File {host.hostname}:{path} does not exist")


def remote_path_info(host: Host, path, hide: bool = True):
    """
    Returns the size and last modified time of either a file or directory.
    If the path does not exist, FileNotFoundError is raised.
    The function returns dictionary containing:
        *path,
        *size in bytes
        *last modified date as datetime
        *is_dir, bool that specifies whether the path is a dir or not
    :param host: target host
    :param path: target path
    :param hide: controls whether the output will be printed to stdout
    :return: dict
    """
    if remote_path_exists(host, path, hide=hide):
        if remote_is_dir(host, path, hide=hide):
            data = remote_dir_info(host, path, hide=hide)
            data["is_dir"] = True
        else:
            data = remote_file_info(host, path, hide=hide)
            data["is_dir"] = False
        return data
    else:
        raise FileNotFoundError(f"Error. Path {host.hostname}:{path} does not exist")


def remote_file_exists(host: Host, path, hide: bool = True):
    """
    Tests whether given file exists on remote host.
    :param host: target host
    :param path: target path
    :param hide: controls whether the output will be printed to stdout
    :return: bool
    """
    tst = host.run(f"test -f {path} && echo 0 || echo 1", hide=hide).stdout.strip()
    return tst == "0"


def remote_dir_exists(host, path, hide: bool = True):
    """
    Tests whether given directory exists on remote host.
    :param host: target host
    :param path: target path
    :param hide: controls whether the output will be printed to stdout
    :return: bool
    """
    tst = host.run(f"test -d {path} && echo 0 || echo 1", hide=hide).stdout.strip()
    return tst == "0"


def remote_path_exists(host, path, hide: bool = True):
    """
    Tests whether specified path exists on remote host.
    :param host: target host
    :param path: target path
    :param hide: controls whether the output will be printed to stdout
    :return: bool
    """
    tst = host.run(f"test -e {path} && echo 0 || echo 1", hide=hide).stdout.strip()
    return tst == "0"


def rename_remote_file(host, file, new_name, overwrite: bool = True, hide: bool = True):
    """
    Renames a remote file to a new name. Does **NOT** move the file outside its directory.
    If the file does not exist, FileNotFoundError is raised.
    :param host: Target host
    :param file: Path to file to rename
    :param new_name: New name
    :param overwrite: if true, the function will overwrite existing file
    :param hide: controls whether the output will be printed to stdout
    :return: None
    """
    if remote_path_exists(host, file, hide=hide):
        dirname = os.path.dirname(file)
        new_path = f"{dirname}/{new_name}"
        if overwrite:
            host.run(f"mv {file} {new_path}", hide=hide)
        else:
            if remote_file_exists(host, new_path, hide=hide):
                raise FileExistsError(f"Error renaming remote file. \n"
                                      f"File {host.hostname}:{new_path} already exists!")
    else:
        raise FileNotFoundError(f"Error renaming remote file. \n"
                                f"File {host.hostname}:{file} does not exist!")


def rename_remote_dir(host, rdir, new_name, hide: bool = True):
    """
    Renames a remote directory to a new name. Does **NOT** move it to other directory.
    Unlike file, it is impossible to overwrite existing remote directory.
    :param host: Target host
    :param rdir: Remote directory
    :param new_name: New name
    :param hide:
    :return:
    """
    if remote_path_exists(host, rdir, hide=hide):
        # add the trailing / denoting a directory in case it's not there
        if not rdir[-1] == "/":
            rdir += "/"
        new_path = rdir.split('/')[:-2] + [new_name]
        new_path = "/".join(new_path)
        if remote_dir_exists(host, new_path, hide=hide):
            raise FileExistsError(f"Error renaming remote directory. \n"
                                  f"Directory {host.hostname}:{new_path} already exists!")
        else:
            host.run(f"mv {rdir} {new_path}", hide=True)
    else:
        raise FileNotFoundError(f"Error renaming remote directory. \n"
                                f"Directory {host.hostname}:{rdir} does not exist!")


def move_remote_file(host: Host, src, dest, overwrite: bool = True, hide: bool = True):
    """
    Moves a remote file to a different directory on remote host. Behaves by default like mv command
    :param host: target host
    :param src: path to file to be moved
    :param dest: new path
    :param overwrite: if true, the function will overwrite already existing destination file
    :param hide:
    :return:
    """

    if remote_file_exists(host, src, hide=hide):
        if remote_file_exists(host, dest, hide=True):
            if not overwrite:
                raise FileExistsError(f"Error moving remote file. \n"
                                      f"Destination file {host.hostname}:{dest} already exists")
        touch_remote(host, dest, hide=hide)  # make sure file and dirs exits
        host.run(f"mv {src} {dest}", hide=hide)
    else:
        raise FileNotFoundError(f"Error moving remote file. \n"
                                f"File {host.hostname}:{src} does not exist!")


def move_remote_dir(host: Host, src, dest, hide: bool = True):
    """
    Moves remote directory to a new path. Since this command works for directories
    the function will add eventually missing "/" at the end of the dest path, making it
    unequivocally a directory to the mv command. Overwriting is not supported.
    :param host: target host
    :param src: path to directory to be moved
    :param dest: path where the directory will be moved
    :param hide: controls whether the output will be printed to stdout
    :return:
    """
    # add / to path if missing, in order for mv treat the path as directory
    if dest[-1] != "/":
        dest += "/"

    if remote_dir_exists(host, src, hide=hide):
        if remote_dir_exists(host, dest, hide=hide):
            raise FileExistsError(f"Error moving remote directory. \n"
                                  f"Destination directory {host.hostname}:{dest} already exists")
        remote_mkdir(host, dest, hide=hide)  # make sure file and dirs exits
        host.run(f"mv {src} {dest}", hide=hide)
    else:
        raise FileNotFoundError(f"Error moving remote file. \n"
                                f"File {host.hostname}:{src} does not exist!")


def copy_remote_file(host: Host, src, dest, overwirte=True, hide: bool = True):
    """
    Copies remote file to a new location on the remote system. Creates the subdirectories
    if necessary. By default, it will overwrite existing destination file.
    :param host: target host
    :param src: path to file to be copied
    :param dest: path, where the file will be copied
    :param hide: controls whether the output will be printed to stdout
    :return:
    """

    if remote_file_exists(host, src, hide=hide):
        if remote_file_exists(host, dest, hide=True):
            if not overwirte:
                raise FileExistsError(f"Error copying remote file. \n"
                                      f"Destination file {host.hostname}:{dest} already exists")
        touch_remote(host, dest, hide=hide)  # make sure file and dirs exits
        host.run(f"cp {src} {dest}", hide=hide)
    else:
        raise FileNotFoundError(f"Error cp remote file. \n"
                                f"File {host.hostname}:{src} does not exist!")


def copy_remote_dir(host, src, dest, hide: bool = True):
    """
    Copies remote directory to a new path. Since this command works for directories
    the function will add eventually missing "/" at the end of the dest path, making it
    unequivocally a directory to the cp command. Overwriting is not supported.
    :param host: target host
    :param src: path to directory to be copied
    :param dest: path, where the directory will be copied
    :param hide: controls whether the output will be printed to stdout
    :return:
    """
    # add / to path if missing, in order for mv treat the path as directory
    if dest[-1] != "/":
        dest += "/"

    if remote_dir_exists(host, src, hide=hide):
        if remote_dir_exists(host, dest, hide=hide):
            raise FileExistsError(f"Error copying remote directory. \n"
                                  f"Destination directory {host.hostname}:{dest} already exists")
        remote_mkdir(host, dest, hide=hide)  # make sure file and dirs exits
        host.run(f"cp -r {src} {dest}", hide=hide)
    else:
        raise FileNotFoundError(f"Error moving remote file. \n"
                                f"File {host.hostname}:{src} does not exist!")


def download_file(host: Host, rem_file, dest=None, overwrite=True):
    """
    Downloads a remote file from remote host. Creates necessary subdirectories.
    By default, if dest is already existing file, it will be overwritten. Destination
    can be either file or directory. If destination is not provided, the file will be
    downloaded to user's download directory.
    :param host: target host
    :param rem_file: path to file to download
    :param dest: path where the file will be downloaded
    :param overwrite: if True, overwrite existing destination file
    :return:
    """
    if remote_file_exists(host, rem_file):
        if dest is None:
            # If no destination path is provided, download to user's download directory
            dl_dir = Path.home() / "Downloads"
            fname = Path(rem_file).name
            dest = Path(dl_dir, fname)
        else:
            # Destination has been provided. Now it needs to be checked
            # whether the destination exists.
            if not os.path.exists(dest):
                # If the dest does not exist, we need to decide whether it's a directory
                # a or file: if the dest ends with / or \, it denotes a directory path
                if dest[-1] == "/" or dest[-1] == "\\":
                    # if dest is directory, keep original file name
                    fname = Path(rem_file).name
                    dest = Path(dest, fname)
                # else, dest is already a file
            else:
                # if dest exist, it might be a dir, therfore we keep the original name
                if os.path.isdir(dest):
                    fname = Path(rem_file).name
                    dest = Path(dest, fname)
                # else, dest is file, and will be dealt with according to overwrite
        if overwrite:
            host.download(rem_file, dest=str(dest))
        else:
            raise FileExistsError(f"Error downloading file. \n"
                                  f"Destination file {dest} already exists")
    else:
        raise FileNotFoundError(f"Error downloading file. \n"
                                f"File {host.hostname}:{rem_file} does not exist!")


def download_dir(host: Host, rem_path, dest_path=None):
    """
    Download a remote directory from remote host. Default destination is user's download directory.
    Necessary subdirectories will be created.
    :param host: target host
    :param rem_path: path to remote directory
    :param dest_path: path to local directory where the remote directory will be downloaded
    :return:
    """
    if remote_dir_exists(host, rem_path):
        if remote_is_dir(host, rem_path):
            pass
        else:
            raise FileNotFoundError(f"Error downloading directory. \n"
                                    f"Remote directory {host.hostname}:{rem_path} is not a directory")
    else:
        raise FileNotFoundError(f"Error downloading directory. \n"
                                f"Remote directory {host.hostname}:{rem_path} does not exist!")

    if dest_path is None:
        dirname = os.path.basename(os.path.normpath(rem_path))
        dest_path = Path.home() / "Downloads" / dirname

    # Step 1: Get all directories and create them locally
    dir_result = host.run(f"find {rem_path} -type d", hide=True)
    remote_dirs = dir_result.stdout.strip().split('\n')

    for remote_subdir in remote_dirs:
        relative_path = os.path.relpath(remote_subdir, rem_path)
        local_subdir = os.path.join(dest_path, relative_path)
        os.makedirs(local_subdir, exist_ok=True)
        # print(f"Created local directory: {local_subdir}")

    # Step 2: Get all files and download them
    file_result = host.run(f"find {rem_path} -type f", hide=True)
    remote_files = file_result.stdout.strip().split('\n')

    for remote_file in remote_files:
        relative_path = os.path.relpath(remote_file, rem_path)
        local_file_path = os.path.join(dest_path, relative_path)
        host.download(remote_file, dest=local_file_path)
        # print(f"Downloaded: {remote_file} → {local_file_path}")


def delete_remote_file(host:Host, path):
    """
    Deletes a remote file if it exists on the host. If not, FileNotFound Error will be raised.
    :param host: target host
    :param path: path to file to be deleted
    :return:
    """
    if remote_file_exists(host, path):
        host.run(f"rm {path}")
    else:
        raise FileNotFoundError(f"Error deleting remote file. \n"
                                f"File {host.hostname}:{path} does not exist")


def delete_remote_dir(host:Host, path):
    """
    Deletes remote directory, if it exists on the host. If not, FileNotFound Error will be raised.
    :param host:
    :param path:
    :return:s
    """
    if remote_dir_exists(host, path):
        host.run(f"rm -rf {path}")
    else:
        raise FileNotFoundError(f"Error deleting remote directory."
                                f"Directory {host.hostname}:{path} does not exist")


def truncate_remote_file(host:Host, path):
    """
    Truncates (deletes content) of a file on a remote host if it exists
    :param host: target host
    :param path: path to file to be truncated
    :return:
    """
    if remote_file_exists(host, path):
        host.run(f"truncate --size 0 {path}")
    else:
        raise FileNotFoundError(f"Error truncating remote file."
                                f"File {host.hostname}:{path} does not exist")

def delete_remote_dir_content(host:Host, path):
    """
    Deletes all files in the given remote directory. If the directory does not exist, FileNotFound Error will be raised.
    :param host: target host
    :param path: path to directory to be deleted
    :return:
    """
    if remote_file_exists(host, path):
        host.run(f"rm -rf {path}/*")
    else:
        raise FileNotFoundError(f"Error deleting remote directory content."
                                f"Directory {host.hostname}:{path} does not exist")


def upload_file(host:Host, file, rem_dest):
    """
    Uploads local file to remote host
    :param host: target host
    :param file: path to local file to be uploaded
    :param rem_dest: path on the remote where the file will be uploaded
    :return:
    """
    if os.path.exists(file):
        if rem_dest[-1] == "/":
            # rem_dest is a directory => keep original file name
            fname = os.path.basename(file)
            rem_dest = rem_dest[:-1] + fname
        # else, rem_dest is file and can be used for upload
        host.upload(file, rem_dest)

    else:
        raise FileNotFoundError(f"Error uploading file. \nFile {file} does not exist")



def upload_dir(host:Host, local_dir, dest_dir):
    # TODO
    pass


def zip_remote_dir(host:Host, dir_path):
    """
    Creates an archive (tar) of a directory and stores in "next to" the target directory.
    E.g. if dir_path = /mnt/data/logs/ , this function will create an archive that contains
    the logs directory and store the archive as /mnt/data/logs.tar
    :param host:
    :param dir_path:
    :return: path of the created archive.
    """
    if not remote_path_exists(host, dir_path):
        raise FileNotFoundError(f"Error creating archive. \n"
                                f"Directory {host.hostname}:{dir_path} does not exist")
    if not remote_is_dir(host, dir_path):
        raise FileNotFoundError(f"Error creating archive. \n"
                                f"{host.hostname}:{dir_path} is not directory")

    if dir_path[-1] != "/":
        dir_path = dir_path + "/"

    tar_fname = os.path.basename(os.path.normpath(dir_path)) + ".tar"
    tar_dir = "/".join(dir_path.split("/")[:-2])
    tar_path = "/".join([tar_dir, tar_fname])
    host.run(f"tar -a -cf {tar_path} -C {dir_path} .")
    return tar_path


def zip_and_download(host:Host, remote_dir, dest=None):
    """
    Zips and a remote directory and downloads the resulting archive to local machine.
    :param host:
    :param remote_dir:
    :param dest:
    :return:
    """
    # if dest is None:
    #     dest = Path.home() / "Downloads"
    archive = zip_remote_dir(host, remote_dir)
    download_file(host, archive, dest)


def read_remote_json(host:Host, remote_path):
    """
    Reads a remote JSON file and returns its content as a Python dictionary.
    :param host: target host
    :param remote_path: The full path to the remote JSON file.
    :return: A Python dictionary containing the JSON data.
    """
    if remote_file_exists(host, remote_path):
        # Open the remote file via SFTP
        with host.conn.sftp().open(remote_path, 'r') as remote_file:
            data = remote_file.read().decode('utf-8')  # Read and decode file content

        # Parse JSON into Python dictionary
        return json.loads(data)
    else:
        raise FileNotFoundError(f"Error reading remote file. \nFile {host.hostname}:{remote_path} does not exist")
