from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Car, Booking
from datetime import datetime
import uuid
import hmac
import hashlib
import base64
import json
from django.db.models import Sum

# --------------------------
# Home Page
# --------------------------
@login_required(login_url='login')
def home(request):
    cars = Car.objects.all().order_by("-created_at")
    return render(request, "rentalapp/home.html", {"cars": cars})


# --------------------------
# Add Car
# --------------------------
@login_required(login_url='login')
def car(request):
    if request.method == "POST":
        Car.objects.create(
            brand=request.POST.get("brand"),
            name=request.POST.get("name"),
            image=request.FILES.get("image"),
            color=request.POST.get("color"),
            model_year=request.POST.get("model_year"),
            transmission=request.POST.get("transmission"),
            car_type=request.POST.get("car_type"),
            price=request.POST.get("price"),
            description=request.POST.get("description"),
        )
        messages.success(request, "Car added successfully ✅")
        return redirect("home")
    return render(request, "rentalapp/car.html")


# --------------------------
# Update Car
# --------------------------
@login_required(login_url='login')
def update_car(request, id):
    car = get_object_or_404(Car, id=id)
    if request.method == "POST":
        car.brand = request.POST.get("brand")
        car.name = request.POST.get("name")
        if request.FILES.get("image"):
            car.image = request.FILES.get("image")
        car.color = request.POST.get("color")
        car.model_year = request.POST.get("model_year")
        car.transmission = request.POST.get("transmission")
        car.car_type = request.POST.get("car_type")
        car.price = request.POST.get("price")
        car.description = request.POST.get("description")
        car.save()
        messages.success(request, "Car updated successfully ✏️")
        return redirect("home")
    return render(request, "rentalapp/car.html", {"car": car})


# --------------------------
# Delete Car
# --------------------------
@login_required(login_url='login')
def delete_car(request, id):
    car = get_object_or_404(Car, id=id)
    car.delete()
    messages.success(request, "Car deleted successfully 🗑️")
    return redirect("home")


# --------------------------
# Car Detail Page
# --------------------------
def car_detail(request, id):
    car = get_object_or_404(Car, id=id)
    return render(request, "car_detail.html", {"car": car})


# --------------------------
# Booking Page
# --------------------------
@login_required
def book_car(request, id):
    car = get_object_or_404(Car, id=id)

    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()

            if end < start:
                messages.error(request, "End date cannot be before start date.")
                return redirect('book_car', id=id)

        except:
            messages.error(request, "Invalid date format.")
            return redirect('book_car', id=id)

        Booking.objects.create(
            user=request.user,
            vehicle=car,
            start_date=start,
            end_date=end
        )

        messages.success(request, f"{car.name} booked successfully!")
        return redirect("booking_success")

    return render(request, "rentalapp/my_booking.html", {"car": car})


# --------------------------
# Booking Success Page
# --------------------------
@login_required
def booking_success(request):

    if "data" in request.GET:
        try:
            decoded = base64.b64decode(request.GET.get("data")).decode()
            response = json.loads(decoded)

            if response.get("status") == "COMPLETE":
                messages.success(request, "Payment Successful 🎉")
            else:
                messages.error(request, "Payment Failed ❌")

        except Exception as e:
            print(e)

    bookings = Booking.objects.filter(user=request.user).order_by("-id")

    # ✔ Only latest approved booking
    approved_booking = Booking.objects.filter(
        user=request.user,
        status="Approved"
    ).order_by("-id").first()

    if approved_booking:
        total_amount = approved_booking.total_price
    else:
        total_amount = 0

    transaction_uuid = str(uuid.uuid4())
    product_code = "EPAYTEST"

    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"

    secret_key = "8gBm/:&EnhH.1/q"

    hash_object = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    )

    signature = base64.b64encode(hash_object.digest()).decode()

    context = {
        "bookings": bookings,
        "total_amount": total_amount,
        "transaction_uuid": transaction_uuid,
        "product_code": product_code,
        "signature": signature,
    }

    return render(request, "rentalapp/booking_success.html", context)

# --------------------------
# Delete Booking
# --------------------------
@login_required
def delete_booking(request, id):
    booking = get_object_or_404(Booking, id=id, user=request.user)
    booking.delete()
    messages.success(request, "Booking deleted successfully 🗑️")
    return redirect("booking_success")


# --------------------------
# Approve Booking
# --------------------------
@login_required
def approve_booking(request, id):
    booking = get_object_or_404(Booking, id=id)
    booking.status = "Approved"
    booking.save()
    messages.success(request, "Booking Approved")
    return redirect("booking_success")


# --------------------------
# Reject Booking
# --------------------------
@login_required
def reject_booking(request, id):
    booking = get_object_or_404(Booking, id=id)
    booking.status = "Cancelled"
    booking.save()
    messages.error(request, "Booking Rejected ❌")
    return redirect("booking_success")


# --------------------------
# Search Cars
# --------------------------
@login_required(login_url='login')
def search(request):
    brand = request.GET.get("brand")
    car_type = request.GET.get("car_type")
    color = request.GET.get("color")
    transmission = request.GET.get("transmission")

    cars = Car.objects.all().order_by("-created_at")

    if brand:
        cars = cars.filter(brand__icontains=brand)
    if car_type:
        cars = cars.filter(car_type__icontains=car_type)
    if color:
        cars = cars.filter(color__icontains=color)
    if transmission:
        cars = cars.filter(transmission__icontains=transmission)

    # Unique brands for dropdown
    brands = Car.objects.values_list('brand', flat=True).distinct()
    car_types = ["Petrol", "Diesel", "Hybrid", "Electric"]
    colors = ["Black", "White", "Silver", "Red", "Blue"]
    transmissions = ["Manual", "Automatic"]

    context = {
        "cars": cars,
        "brands": brands,
        "car_types": car_types,
        "colors": colors,
        "transmissions": transmissions,
    }
    return render(request, "rentalapp/search.html", context)


# --------------------------
# Login View
# --------------------------
class LoginViewCustom(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, "login.html", {"form": form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username} 👋")
            return redirect("home")
        messages.error(request, "Invalid username or password ❌")
        return render(request, "login.html", {"form": form})


# --------------------------
# Logout View
# --------------------------
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully 👋")
    return redirect("login")
