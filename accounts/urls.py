from django.urls import path
from accounts import views

urlpatterns = [
    path('user/',views.UserListView.as_view()),
    path('user/info/',views.LoggedInUserDetailView.as_view()),
    path('register/',views.RegisterView.as_view()),
    path('sendcode/',views.sendcode_view),
    path('login/',views.UserSigninAPIView.as_view()),
]