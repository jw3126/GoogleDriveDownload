import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import GoogleDriveFile

def isfolder(file):
    return file['mimeType']=='application/vnd.google-apps.folder'
    
def isfile(file):
    return not isfolder(file)

def get_filename(file):
    return file["title"]

def get_files_recursive(drive, parent):
    print("get_files_recursive {}".format(parent))
    d = dict()
    file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % parent}).GetList()
    for file in file_list:
        key = file['title']
        if isfolder(file):
            d[key] = get_files_recursive(drive, file['id'])
        else:
            d[key] = file
    return d

def get_filetree(drive):
    parent = 'root'
    return get_files_recursive(drive, parent)

def download_file(path, file):
    msg = "download_file(path={}, file={})".format(path, get_filename(file))
    print(msg)
    try:
        file.GetContentFile(path)
    except Exception as e:
        print("Got {} while downloading {}.".format(e, path))
    
def download_tree(rootpath, tree):
    os.makedirs(rootpath, exist_ok=True)
    for (key, file) in tree.items():
        path = os.path.join(rootpath, key)
        if isinstance(file, GoogleDriveFile):
            if os.path.exists(path):
                print(path, "exists already, skip")
            else:
                download_file(path, file)
        elif (type(file) == dict):  # GoogleDriveFile subclasses dict ouch!
            download_tree(path, file)
        else:
            print("Not sure what to ", key, type(file))


if __name__ == "__main__":
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
    drive = GoogleDrive(gauth)
    print("drive={}".format(drive))
    tree = get_filetree(drive)
    download_tree("dump", tree)
