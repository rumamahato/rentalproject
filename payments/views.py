from django.shortcuts import render
from rentalapp.models import Car, Booking       # rentalapp models
from .models import Transaction                 # payments models
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import base64, json, hashlib, hmac

@login_required
def success_esewa(request):

    data = request.GET.get("data")

    if not data:
        return HttpResponse("No payment data received")

    try:
        decoded = base64.b64decode(data).decode()
        response = json.loads(decoded)

        transaction_code = response.get("transaction_code")
        status = response.get("status")
        total_amount = response.get("total_amount")
        transaction_uuid = response.get("transaction_uuid")
        product_code = response.get("product_code")

        if status == "COMPLETE":

            Transaction.objects.create(
                user=request.user,
                transaction_code=transaction_code,
                transaction_uuid=transaction_uuid,
                product_code=product_code,
                total_amount=total_amount,
                status=status
            )

            return render(request,"payments/success.html",{
                "amount": total_amount
            })

        else:
            return render(request,"payments/failure.html")

    except Exception as e:
        return HttpResponse(str(e))


@login_required
def failure_esewa(request):
    return render(request,"payments/failure.html")