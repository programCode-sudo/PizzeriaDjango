from django.urls import path
from .views import AddFoodItemToRestaurantView,GetAllFoodItemsView,GetOneFoodItemView,DeleteFoodItemView,EditFoodItemView,GetOneFoodItemByIdView

urlpatterns = [
    path('add_food_item/', AddFoodItemToRestaurantView.as_view(), name='add_food_item_to_restaurant'),
    path('getFoodItems/',GetAllFoodItemsView.as_view(),name='getfooditem'),
    path('getOneFood/',GetOneFoodItemView.as_view(),name='getonefood'),
    path('deleteFoodItem/<int:food_item_id>/',DeleteFoodItemView.as_view(),name='deletefooditem'),
    path('editFoodItem/<int:food_item_id>/',EditFoodItemView.as_view(),name='editfooditem'),
    path('getFoodItemById/<int:food_item_id>/',GetOneFoodItemByIdView.as_view(),name='getFoodById')
]
