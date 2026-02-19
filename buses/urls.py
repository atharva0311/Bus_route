from django.urls import path
from . import views

app_name = 'buses'

urlpatterns = [
    path('search/', views.BusSearchView.as_view(), name='search'),
    path('<int:pk>/', views.BusDetailView.as_view(), name='detail'),

    # existing APIs
    path('api/routes/', views.get_routes_json, name='routes_api'),
    path('api/seats/<int:bus_id>/', views.get_available_seats, name='seats_api'),

    # ======================
    # NEW APIs
    # ======================
    path('api/fare/<int:bus_id>/', views.fare_preview_api, name='fare_api'),
    path('api/live-location/<int:bus_id>/', views.live_location_api, name='live_location_api'),
]
