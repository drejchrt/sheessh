from src.sheessh.sheessh import *

ID_075 = r"C:\Users\REJD\.ssh\id_rsa_075"
ID_087 = r"C:\Users\REJD\.ssh\id_rsa_087"

host = Host(
    # hostname="TS20-4790010",
    # hostname="TS20-3795167",
    # hostname="TS20-4790005",
    hostname="TS20-4790007",
    identity=ID_075
)

print(test_connection(host))

# result = ssh(host,"ps afx")

# touch_remote(host, "/mnt/data/rejd/tbyp.proof")

# print(remote_is_dir(host, "/mnt/data/rejd"))
# print(remote_is_dir(host, "/mnt/data/rejd/"))
# print(remote_is_dir(host, "/mnt/data/rejd/.bashrc-20"))

# print(remote_file_info(host, "/mnt/data/rejd/.bashrc-ts20"))
# print(remote_file_info(host, "/mnt/data/rejd/"))
# print(remote_file_info(host, "/mnt/data/rejd/.bashrc-20"))

# print(remote_dir_info(host,"/mnt/data/rejd/"))
# print(remote_dir_info(host,"/mnt/data/rejd"))
# print(remote_dir_info(host,"/mnt/data/rejd/.bashrc-ts20"))
# print(remote_dir_info(host,"/mnt/data/rejd/.bashrc-20"))
#

# print(remote_file_exists(host,"/mnt/data/rejd/"))
# print(remote_file_exists(host,"/mnt/data/rejd"))
# print(remote_file_exists(host,"/mnt/data/rejd/bass"))
# print(remote_file_exists(host,"/mnt/data/rejd/.bashrc-ts20"))

# print(remote_dir_exists(host,"/mnt/data/rejd/"))
# print(remote_dir_exists(host,"/mnt/data/rejd"))
# print(remote_dir_exists(host,"/mnt/data/rejd/bass"))
# print(remote_dir_exists(host,"/mnt/data/rejd/.bashrc-ts20"))

# touch_remote(host,"/mnt/data/rejd/tst/foo.bar")
# print(remote_file_exists(host,"/mnt/data/rejd/tst/foo.bar"))
# rename_remote_file(host,"/mnt/data/rejd/tst/foo.bar", "baz.bag")
# print(remote_file_exists(host,"/mnt/data/rejd/tst/foo.bar"))
# print(remote_file_exists(host,"/mnt/data/rejd/tst/baz.bag"))

# touch_remote(host,"/mnt/data/rejd/tst/foo.bar")
# print(remote_dir_exists(host,"/mnt/data/rejd/tst/"))
# rename_remote_dir(host,"/mnt/data/rejd/tst/","teeeeest")
# print(remote_dir_exists(host,"/mnt/data/rejd/tst/"))
# print(remote_dir_exists(host,"/mnt/data/rejd/teeeeest/"))

# touch_remote(host, "/mnt/data/rejd/tst/foo.bar")
# move_remote_file(host, "/mnt/data/rejd/tst/foo.bar", "/tmp/data/rejd/test/" )
# touch_remote(host, "/mnt/data/rejd/tst/foo.bar")
# move_remote_file(host, "/mnt/data/rejd/tst/foo.bar", "/tmp/data/rejd/tst/baz.bar" )

# touch_remote(host,"/mnt/data/rejd/tst/foo.bar")
# move_remote_dir(host, "/mnt/data/rejd/tst/","/tmp/data")
# move_remote_dir(host, "/mnt/data/rejd/tst/","/tmp/data/rejd")

# dest_dir = os.path.join(os.getcwd(), ".tst")
# os.makedirs(dest_dir)
# dest_file = os.path.join(dest_dir, ".test2.txt")
# touch_remote(host, "/mnt/data/rejd/tst/test.txt")
# download_file(host, "/mnt/data/rejd/tst/test.txt")
# download_file(host, "/mnt/data/rejd/tst/test.txt", dest=dest_dir)
# download_file(host, "/mnt/data/rejd/tst/test.txt", dest=dest_file)

# dest_dir = os.path.join(os.getcwd(), ".tst")
# os.makedirs(dest_dir, exist_ok=True)
# download_dir(host,"/mnt/data/rejd/tst")
# download_dir(host,"/mnt/data/rejd/tst",dest_dir)

# delete_remote_file(host, "/mnt/data/rejd/tst.tar")

#print(zip_remote_dir(host, "/mnt/data/rejd/tst"))

# zip_and_download(host,"/mnt/data/rejd/tst")