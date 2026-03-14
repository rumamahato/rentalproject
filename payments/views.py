from django.shortcuts import render
from rentalapp.models import Booking
from .models import Transaction
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import base64
import json

@login_required
def success_esewa(request):
    data = request.GET.get("data")
    if not data:
        return HttpResponse("No payment data received")

    try:
        # Decode the base64 payment data
        decoded = base64.b64decode(data).decode()
        response = json.loads(decoded)

        transaction_code = response.get("transaction_code")
        status = response.get("status")
        total_amount = response.get("total_amount")
        transaction_uuid = response.get("transaction_uuid")
        product_code = response.get("product_code")

        # ✅ Prevent duplicate transaction
        if not Transaction.objects.filter(transaction_uuid=transaction_uuid).exists():
            Transaction.objects.create(
                user=request.user,
                transaction_code=transaction_code,
                transaction_uuid=transaction_uuid,
                product_code=product_code,
                total_amount=total_amount,
                status=status
            )

        # Update Booking if COMPLETE
        if status == "COMPLETE":
            booking_id = request.session.get("selected_booking")
            if booking_id:
                booking = Booking.objects.filter(id=booking_id, user=request.user).first()
                if booking:
                    booking.status = "Paid"
                    booking.save()
                request.session.pop("selected_booking", None)

            # Render success box
            context = {
                "transaction_code": transaction_code,
                "amount": total_amount
            }
            return render(request, "payments/success.html", context)

        else:
            return render(request, "payments/failure.html")

    except Exception as e:
        return HttpResponse(f"Error processing payment: {str(e)}")


@login_required
def failure_esewa(request):
    return render(request, "payments/failure.html")