import shutil
import os
from wsgiref.util import FileWrapper

from django.conf import settings
from django.http import HttpResponse
from django.utils.encoding import escape_uri_path

def make_tmp_archive(folder):
    static_folder = settings.BASE_DIR

    upload_path = os.path.join(static_folder, "media")
    tmp_dir_path = os.path.join(upload_path, folder.Name)

    if os.path.exists(tmp_dir_path):
        try:
            shutil.rmtree(tmp_dir_path)
        except OSError:
            return None

    if recursive_file_copy(upload_path, folder):
        try:
            path_zip = shutil.make_archive(tmp_dir_path, "zip", tmp_dir_path)
            response = HttpResponse(FileWrapper(open(path_zip, 'rb')), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{escape_uri_path(folder.Name.replace(" ", "_")+".zip")}"'
            shutil.rmtree(tmp_dir_path)
            return response
        except OSError:
            return None
    else:
        return None


def recursive_file_copy(folder_name, folder):
    path = os.path.join(folder_name, folder.Name)
    try:
        os.mkdir(path)
    except OSError:
        return None

    files = folder.Files.all()
    for file in files:
        newfile = os.path.join(path, file.Name)
        try:
            shutil.copy(file.FileData.path, newfile)
        except OSError:
            return None

    subfolders = folder.SubFolders.all()

    for subfolder in subfolders:
        if recursive_file_copy(path, subfolder) is None:
            return None

    return True
