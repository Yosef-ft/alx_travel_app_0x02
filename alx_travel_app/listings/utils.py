import uuid
import requests
from django.conf import settings

def initiate_chapa_payment(booking, user):
    tx_ref = str(uuid.uuid4())
    amount = booking.total_price
    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": user.email,
        "tx_ref": tx_ref,
        "return_url": f"http://localhost:8000/payment/verify/{tx_ref}/",
        "callback_url": f"http://localhost:8000/payment/verify/{tx_ref}",
        "customization": {"title": "Travel Booking", "description": f"Booking ID {booking.id}"}
    }

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
    }

    response = requests.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)
    data = response.json()

    if data.get('status') == 'success':
        return {
            "tx_ref": tx_ref,
            "checkout_url": data['data']['checkout_url']
        }
    else:
        raise Exception(data.get("message", "Failed to initiate payment"))
