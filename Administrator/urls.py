from django.urls import path
from .views import DeleteUserView,GetAllUsersView

urlpatterns = [
    path('deleteUser/',DeleteUserView.as_view(),name='delete_user'),
    path('getUsers/',GetAllUsersView.as_view(),name='get_all_users')
]
