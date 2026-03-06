from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import base64, json, hashlib, hmac

from .models import Transaction


@login_required(login_url='log_in')
def success_esewa(request):
    # 1️⃣ Get encoded data from eSewa
    encoded_data = request.GET.get("data")
    if not encoded_data:
        return HttpResponse("Invalid response", status=400)

    # 2️⃣ Decode Base64 → JSON
    try:
        decoded_json = base64.b64decode(encoded_data).decode("utf-8")
        payload = json.loads(decoded_json)
    except Exception:
        return HttpResponse("Invalid data format", status=400)

    # 3️⃣ Verify Signature
    try:
        signed_fields = payload["signed_field_names"].split(",")

        message = ",".join(
            [f"{field}={payload[field]}" for field in signed_fields]
        )

        secret_key = "8gBm/:&EnhH.1/q"   # eSewa TEST secret key

        expected_signature = base64.b64encode(
            hmac.new(
                secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
        ).decode()

        if expected_signature.rstrip("=") != payload["signature"].rstrip("="):
            return HttpResponse("Invalid signature", status=400)

    except KeyError as e:
        return HttpResponse(f"Missing field: {e}", status=400)

    # 4️⃣ Save Transaction (safe way)
    txn, created = Transaction.objects.get_or_create(
        transaction_uuid=payload["transaction_uuid"],
        defaults={
            "transaction_code": payload["transaction_code"],"product_code": payload["product_code"],
            "total_amount": payload["total_amount"],"status": payload["status"],"user": request.user})

    return render(request, "success_esewa.html", {"txn": txn})


def failure_esewa(request):
    return render(request, "failure_esewa.html")