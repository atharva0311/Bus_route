from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BusViewSet,
    RouteViewSet,
    TripViewSet,
    BookingViewSet,
    LiveLocationViewSet,
)

router = DefaultRouter()
router.register(r'buses', BusViewSet)
router.register(r'routes', RouteViewSet)
router.register(r'trips', TripViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'live-locations', LiveLocationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
