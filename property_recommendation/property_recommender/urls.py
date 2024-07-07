# urls.py

from django.urls import path
from .views import home, related_properties, new_home_view, get_traffic_data, get_rooms_data, price_data_final, price_data_api, location_frequency_api
from .views_auth import login_view, logout_view
from . import views

urlpatterns = [
    path('', new_home_view, name='home'),
    path('newhome/', views.new_home_view, name='new_home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('related_properties/', related_properties, name='related_properties'),
    path('api/traffic_data/', get_traffic_data, name='traffic_data'),
    path('api/rooms_data/', get_rooms_data, name='rooms_data'),
    path('search/', views.home, name='property_search'),     
    path('api/location_frequency_api/', views.location_frequency_api, name='location_frequency_api'),
    path('api/price_data_final/', price_data_final, name='price_data_final'),
    path('api/price_data_new/', price_data_api, name='price_data_api'),
]
