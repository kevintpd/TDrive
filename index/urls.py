from django.urls import path
from . import views

urlpatterns = [

    path('android_app_download/', views.android_app_download, name="android_app_download"),
path("",views.index),
]