from django.urls import path
from . import views


urlpatterns = [

    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout_view'),
    path('my_autocomplete/', views.my_autocomplete, name='my_autocomplete'),
    path('consume_food/', views.consume_food, name='consume_food'),
    path('delete_consumed_food/', views.delete_consumed_food, name='delete_consumed_food'),
    path('nutrient_history/', views.nutrient_history, name='nutrient_history'),
    
]