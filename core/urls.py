from django.urls import path
from . import views
urlpatterns = [
    path('folders/', views.FolderListView.as_view()),
    path('folders/<str:pk>/', views.FolderDetailView.as_view({'get': 'retrieve'})),
    path('files/', views.FileListView.as_view()),
    path('files/<str:pk>/', views.FileDetailView.as_view()),
    path('items/', views.ItemListView.as_view()),
    path('filedownload/<str:id>/', views.FileDownloadView.as_view()),
    path('folderdownload/<str:id>/', views.FolderDownloadView.as_view()),
]