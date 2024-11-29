from django.urls import path
from .views import DeleteUserView,GetUserByIdView,GetAllUsersView,GetUserByUsernameView,EditUserView

urlpatterns = [
    path('deleteUser/',DeleteUserView.as_view(),name='delete_user'),
    path('getUsers/',GetAllUsersView.as_view(),name='get_all_users'),
    path('getUserById/<int:user_id>/',GetUserByIdView.as_view(),name='getuserbyid'),
    path('getUserByUsername/<str:username>/',GetUserByUsernameView.as_view(),name='getuserbyusername'),
    path('editUserById/<int:user_id>/',EditUserView.as_view(),name= 'edituserbyid')
]
