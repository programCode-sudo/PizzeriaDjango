from django.urls import path
from .views import AddToCartView,GetCartItemsView,DeleteCartItemByFoodNameView,AssignPhoneNumberView,CustomerProfileView
from .views import AddLoyaltyPointsView,DeleteLoyaltyPointsView,CreateCouponView,DeleteCouponView,AssignAddressView

urlpatterns = [
    path('addToCart/',AddToCartView.as_view(),name='addtocart'),
    path('getCartItems/',GetCartItemsView.as_view(),name='getcartitems'),
    path('deleteCartItem/<str:food_item_name>/',DeleteCartItemByFoodNameView.as_view(),name='deletecartitem'),
    path('addLoyaltyPoints/<int:customer_id>/',AddLoyaltyPointsView.as_view(),name='addloyaltipoints'),
    path('deleteLoyaltyPoints/<int:customer_id>/',DeleteLoyaltyPointsView.as_view(),name='deleteloyaltypoints'),
    path('addCupon/<int:customer_id>/',CreateCouponView.as_view(),name='addcupon'),
    path('deleteCupon/<int:coupon_id>/',DeleteCouponView.as_view(),name='deletecupon'),
    path('asignPhoneNumber/',AssignPhoneNumberView.as_view(),name='asignphonenumber'),
    path('asignAddress/',AssignAddressView.as_view(),name='asignaddress'),
    path('viewProfile/',CustomerProfileView.as_view(),name='viewprofile')
]
