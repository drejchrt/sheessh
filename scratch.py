from pathlib import Path

from src.sheessh.sheessh import *

def ignore(ex, call, *args, **kwargs):
    try:
        print(call(*args,**kwargs))
    except ex as e:
        print(f"Error [{type(e)}]: {e}")



ID_075 = r"C:\Users\REJD\.ssh\id_rsa_075"
ID_086 = r"C:\Users\REJD\.ssh\id_rsa_086"
ID_087 = r"C:\Users\REJD\.ssh\id_rsa_087"

host = Host(
    # hostname="TS20-4790010",
    # hostname="TS20-3795167",
    # hostname="TS20-4790005",
    # hostname="TS20-4790007",
    hostname="TS20-4790086",
    identity=ID_086
)

print(test_connection(host))


# result = ssh(host,"psa afx", hide=True)
################ test local touch #############################################
# touch("test.txt")
# touch(r"some_bs_dir\\test.txt")

################ test remote touch  ###########################################
# touch_remote(host, "/mnt/data/rejd/tbyp.proof")
# touch_remote(host, "/mnt/data/rejd/tst/tbyp.proof")

################ test remote_mkdir ############################################
# print(remote_mkdir(host, "/mnt/data/rejd/tst0/"))
# print(remote_mkdir(host, "/mnt/data/rejd/tst/tst1"))
# print(remote_mkdir(host, "/mnt/data/rejd/tst2/tst3/tst4"))
# print(remote_mkdir(host, "/mnt/data/rejd/tst5/tst3/tst4/"))

################ test remote_is_dir ###########################################
# print(remote_is_dir(host, "/mnt/data/rejd"))
# print(remote_is_dir(host, "/mnt/data/rejd/"))
# print(remote_is_dir(host, "/mnt/data/rejd/.bashrc-20"))
# print(remote_is_dir(host, "/mnt/data/rejd/.bashrc-ts20"))

################ test remote_file_info #########################################
# ignore(FileNotFoundError, remote_file_info, host,"/mnt/data/rejd/.bashrc-ts20")
# ignore(FileNotFoundError, remote_file_info, host, "/mnt/data/rejd/")
# ignore(FileNotFoundError, remote_file_info, host, "/mnt/data/rejd/.bashrc-20")

################ test remote_dir_info #########################################
# ignore(FileNotFoundError, remote_dir_info,host,"/mnt/data/rejd/")
# ignore(FileNotFoundError, remote_dir_info,host,"/mnt/data/rejd")
# ignore(FileNotFoundError, remote_dir_info,host,"/mnt/data/rejd/.bashrc-ts20")
# ignore(FileNotFoundError, remote_dir_info,host,"/mnt/data/rejd/.bashrc-20")


################ test remote_path_info #########################################
# ignore(FileNotFoundError, remote_path_info, host,"/mnt/data/rejd/.bashrc-ts20")
# ignore(FileNotFoundError, remote_path_info, host, "/mnt/data/rejd/")
# ignore(FileNotFoundError, remote_path_info, host, "/mnt/data/rejd/.bashrc-20")
# ignore(FileNotFoundError, remote_path_info,host,"/mnt/data/rejd/")
# ignore(FileNotFoundError, remote_path_info,host,"/mnt/data/rejd")
# ignore(FileNotFoundError, remote_path_info,host,"/mnt/data/rejd/.bashrc-ts20")
# ignore(FileNotFoundError, remote_path_info,host,"/mnt/data/rejd/.bashrc-20")

################# test rename_remote_file #####################################

# touch_remote(host,"/mnt/data/rejd/tst/test1.txt")
# touch_remote(host,"/mnt/data/rejd/tst/test2.txt")
# rename_remote_file(host,"/mnt/data/rejd/tst/test3.txt", "rst.txt")
# rename_remote_file(host,"/mnt/data/rejd/tst/test1.txt", "test2.txt")

################ test rename_remote_dir #######################################
#rename_remote_dir(host,"/mnt/data/rejd/tst5","tst55")
#rename_remote_dir(host,"/mnt/data/rejd/tst","tst2")
#rename_remote_dir(host,"/mnt/data/rejd/tst2/","tst1")

################ test move_remote_file #########################################
# touch_remote(host,"/mnt/data/rejd/test/blahb.cle")
# move_remote_file(host,"/mnt/data/rejd/test/blahb","/mnt/data/rejd/testt/" )
# move_remote_file(host,"/mnt/data/rejd/test/blahb.cle","/mnt/data/rejd/testt" )
# move_remote_file(host,"/mnt/data/rejd/test/blahb.cle","/mnt/data/rejd/testt/" )
# move_remote_file(host,"/mnt/data/rejd/test/blahb.cle","/mnt/data/rejd/testt/tst" )
# move_remote_file(host,"/mnt/data/rejd/test/blahb.cle","/mnt/data/rejd/testt/tst/" )
# move_remote_file(host,"/mnt/data/rejd/test/blahb.cle","/mnt/data/rejd/testt/tst.txt" )

################ test copy_remote_file ########################################
# touch_remote(host,"/mnt/data/rejd/test/blahb.cle")
# copy_remote_file(host,"/mnt/data/rejd/test/blahb","/mnt/data/rejd/testt/" )
# copy_remote_file(host,"/mnt/data/rejd/test/blahb.cle","/mnt/data/rejd/testt" )
# copy_remote_file(host,"/mnt/data/rejd/test/blahb.cle","/mnt/data/rejd/testt/" )
# copy_remote_file(host,"/mnt/data/rejd/test/blahb.cle","/mnt/data/rejd/testt/tst" )
# copy_remote_file(host,"/mnt/data/rejd/test/blahb.cle","/mnt/data/rejd/testt/tst/" )
# copy_remote_file(host,"/mnt/data/rejd/test/blahb.cle","/mnt/data/rejd/testt/tst.txt" )


################ test download_file ###########################################
# download_file(host,"/mnt/data/rejd/tst/blah")
# download_file(host,"/mnt/data/rejd/tst/blah.txt")
# download_file(host,"/mnt/data/rejd/tst/blah.txt", "dl_tst/")
# download_file(host,"/mnt/data/rejd/tst/blah.txt","dl_tst")
# download_file(host,"/mnt/data/rejd/tst/blah.txt", "dl_tst", overwrite=False)
# download_file(host,"/mnt/data/rejd/tst/blah.txt", "dl_tst/loool.log" )
# download_file(host,"/mnt/data/rejd/tst/blah.txt", "dl_tst/trada/loool.log" )
# download_file(host,"/mnt/data/rejd/tst/blah.txt", "dl_tst/trada/" )
# download_file(host,"/mnt/data/rejd/tst/blah.txt", "dl_tst/trada" )

################ test download_dir ############################################

# download_dir(host, "/mnt/data/rejd/tst")
# download_dir(host, "/mnt/data/rejd/tst/")
# download_dir(host, "/mnt/data/rejd/tst/blah.txt")

# download_dir(host,"/mnt/data/rejd/tst/", "dl_dir_tst")
# download_dir(host,"/mnt/data/rejd/tst/", "dl_dir_tst/propr")
# download_dir(host,"/mnt/data/rejd/tst/", "dl_dir_tst/propr/")
# download_dir(host,"/mnt/data/rejd/tst/", "test")
# download_dir(host,"/mnt/data/rejd/tst/", "test/")

# download_dir(host,"/mnt/data/rejd/tst/", "dl_dir_tst/")

################ test zip_remote_dir ##########################################

# zip_remote_dir(host, "/mnt/data/rejd/tst")
# zip_remote_dir(host, "/mnt/data/rejd/tst/")
# zip_remote_dir(host, "/mnt/data/rejd/.bashrc-ts20")
# zip_remote_dir(host, "/mnt/data/rejd/test")
# zip_remote_dir(host, "/mnt/data/rejd/test/")
# zip_remote_dir(host, "/mnt/data/rejd/test/looool")