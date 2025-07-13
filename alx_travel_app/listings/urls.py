from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, verify_payment, initiate_payment


router = DefaultRouter()
router.register(r'listing', ListingViewSet)
router.register(r'booking', BookingViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('payment/initiate/<int:booking_id>/', initiate_payment, name='initiate-payment'),
    path('payment/verify/<str:tx_ref>/', verify_payment, name='verify-payment'),
]