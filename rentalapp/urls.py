from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("car/", views.car, name="car"),
    path("update_car/<int:id>/", views.update_car, name="update_car"),
    path("delete_car/<int:id>/", views.delete_car, name="delete_car"),
    path("search/", views.search, name="search"),
    path("car/<int:id>/book/", views.book_car, name="book_car"),
    path("booking_success/", views.booking_success, name="booking_success"),
    path("car/<int:id>/", views.car_detail, name="car_detail"),

    # Delete Booking (ADD THIS)
    path("booking/delete/<int:id>/", views.delete_booking, name="delete_booking"),

    # Authentication
    path("login/", views.LoginViewCustom.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
]