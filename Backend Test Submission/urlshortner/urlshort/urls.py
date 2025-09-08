from django.urls import path
from . import views

urlpatterns = [
    path("shorten", views.createshorturl),
    path("shorturlget/<str:code>", views.shorturlget),  
    path("<str:code>", views.redirectshorturl),
]
