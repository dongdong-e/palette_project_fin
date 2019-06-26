from django.contrib import admin
from django.urls import path, include
from . import views


app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('main/', views.main, name='main'),
    path('user/', views.use, name='use'),
    path('upload/', views.upload, name='upload'),
    path('delete/<int:upload_num>/', views.delete, name='delete'),
    path('set_phone_number/<int:upload_num>/', views.set_phone_number, name='set_phone_number'),
    path('confirm/<int:upload_num>/', views.confirm, name='confirm'),
    path('edit/<int:upload_num>/', views.edit, name='edit'),
    path('photo/<int:pk>/<str:random_url>', views.photo, name='photo'),
]