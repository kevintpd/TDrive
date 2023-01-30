from django.urls import path
from . import views
urlpatterns = [
    path('shareitem/', views.ShareItemListView.as_view()),
    path('shareitem/<str:pk>/', views.MyShareDetailView.as_view()),
    path('joinedshare/', views.JoinedShareListView.as_view()),
    path('joinshare/<str:pk>/', views.JoinShareView.as_view()),
    path('AllShare/', views.AllShareListView.as_view()),

    path('createsharefolder/<str:pk>/', views.ShareFolderCreateView.as_view()),
    path('uploadfiletoshare/<str:pk>/', views.ShareFileCreateView.as_view()),
    path('sharefolder/<str:pk>/', views.ShareFolderDetailView.as_view({'get': 'retrieve'})),
    path('sharefile/<str:pk>/', views.ShareFileDetailView.as_view()),
]