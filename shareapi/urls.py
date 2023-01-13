from django.urls import path
from . import views
urlpatterns = [
    path('shareitem/', views.ShareItemListView.as_view()),
    path('shareitem/<str:pk>/', views.MyShareDetailView.as_view({'get': 'retrieve'})),
    path('joinedshare/', views.JoinedShareListView.as_view()),
    path('createsharefolder/', views.ShareFolderCreateView.as_view()),
    path('uploadfiletoshare/', views.ShareFileCreateView.as_view()),
    path('sharefolder/<str:pk>', views.ShareFolderDetailView.as_view()),
    path('sharefile/<str:pk>', views.ShareFileDetailView.as_view()),
]