from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list, name='list'),
    path('book/<int:bus_id>/', views.book_bus, name='book'),
    path('<int:pk>/', views.booking_detail, name='detail'),
    path('<int:pk>/cancel/', views.cancel_booking, name='cancel'),
    path('<int:pk>/track/', views.track_booking, name='track'),

    path("api/seats/<int:bus_id>/", views.seat_layout_api, name="seat_layout_api"),
    path('api/seats/status/<int:bus_id>/', views.booking_seat_status_api, name='seat_status_api'),

    # PayPal Payment URLs
    path("payment/<int:booking_id>/", views.create_payment, name="create_payment"),
    path("payment/success/", views.payment_success, name="payment_success"),
    path("payment/cancel/", views.payment_cancel, name="payment_cancel"),
]
