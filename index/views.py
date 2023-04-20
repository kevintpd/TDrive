from django.shortcuts import render

def index(requests):
    return  render(requests, "index.html")


import os
from django.http import HttpResponse, Http404, FileResponse


def android_app_download(requests):
    response = FileResponse(open("media/test.apk", 'rb'))
    response['content_type'] = "application/octet-stream"
    response['Content-Disposition'] = 'attachment; filename=' + os.path.basename("../media/test.apk")
    return response

    # try:
    #     response = FileResponse(open("../media/test.apk", 'rb'))
    #     response['content_type'] = "application/octet-stream"
    #     response['Content-Disposition'] = 'attachment; filename=' + os.path.basename("../media/test.apk")
    #     return response
    # except Exception:
    #     raise Http404