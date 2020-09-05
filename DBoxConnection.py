from dotenv import load_dotenv
import dropbox
import os
from pprint import pprint


# TODO:
# Refresh token
# List directories


class DBoxConnection:
    load_dotenv()
    def __init__(self):
        self.token = os.getenv('TOKEN')
        self.appkey = os.getenv('APPKEY')
        self.connection = dropbox.Dropbox(self.token)
        self.backupfolder = ""


    def validate_token(self):
        try:
            self.connection.users_get_account()
            print(self.connection.users_get_account())
            print("Valid")
            return True
        except:
            print("Not valid")
            return False


    def get_dirs(self, path, only_names, recursive):
        if only_names:
            return [file.name for file in self.connection.files_list_folder(path, recursive=recursive).entries]
        else:
            return self.connection.files_list_folder(path, recursive=recursive)
            

    def create_folder(self, folder):
        return self.connection.files_create_folder_v2(path=folder)


    def upload_content(self, file, path):
        self.connection.files_upload(file, path=path, mode=dropbox.files.WriteMode("overwrite"))


    def search(self, file, path):
        file = self.connection.files_search(query=file, path=path)
        if file:
            return file
        else:
            return "The file doesn't exist"


    def download_file(self, file, path, download_type=''):
        if download_type == 'zip':
            self.connection.files_download_zip()
        else:
            pass
            self.connection.files_get_preview()