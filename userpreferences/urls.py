from . import views
from django.urls import path, include
from django.urls import path

urlpatterns = [
    path('', views.index, name='preferences')
]
