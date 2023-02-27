from django.urls import path
from . import views
urlpatterns = [
    path('shareitemroot/', views.ShareItemRootListView.as_view({'get': 'list'})),
    path('shareitem/', views.ShareItemListView.as_view()),
    path('shareitem/<str:pk>', views.MyShareDetailView.as_view({'get': 'retrieve'})),

    path('joinedshare/', views.JoinedShareListView.as_view({'get': 'list'})),
    path('joinshare/<str:pk>', views.JoinShareView.as_view()),
    path('quitShare/<str:pk>', views.QuitShareView.as_view()),
    path('AllShare/', views.AllShareListView.as_view({'get': 'list'})),
    path('Refresh/',views.RefreshShareListView.as_view()),


    path('createsharefolder/<str:pk>', views.ShareFolderCreateView.as_view()),
    path('uploadfiletoshare/<str:pk>', views.ShareFileCreateView.as_view()),
    path('sharefolder/<str:pk>', views.ShareFolderDetailView.as_view({'get': 'retrieve'})),
    path('sharefile/<str:pk>', views.ShareFileDetailView.as_view()),

    path('searchsharefile/', views.SearchShareFileView.as_view()),

]