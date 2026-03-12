from django.urls import path
from .views import *

urlpatterns = [
    path("success/", success_esewa, name="success_esewa"),
    path("failure/", failure_esewa, name="failure_esewa"),
]