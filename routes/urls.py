from django.urls import path
from . import views

app_name = 'routes'

urlpatterns = [
    path('list/', views.route_list, name='route_list'),
    path('add/', views.add_route, name='add_route'),
    path('add-stop/', views.add_stop_to_route, name='add_stop'),
    path('delete/<int:route_id>/', views.delete_route, name='delete_route'),
]
