from django.shortcuts import render
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer
from .models import Listing, Booking, Payment
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .utils import initiate_chapa_payment
import requests
from django.conf import settings


class ListingViewSet(ModelViewSet):
    serializer_class = ListingSerializer
    queryset = Listing.objects.all()


class BookingViewSet(ModelViewSet):
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()


@api_view(['POST'])
def initiate_payment(request, booking_id):
    try:
        booking = Booking.objects.get(pk=booking_id)
        user = request.user

        payment_info = initiate_chapa_payment(booking, user)

        payment = Payment.objects.create(
            booking=booking,
            status='Pending',
            amount=booking.total_price,
            chapa_tx_ref=payment_info["tx_ref"],
            chapa_checkout_url=payment_info["checkout_url"]
        )

        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=201)

    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['GET'])
def verify_payment(request, tx_ref):
    try:
        payment = Payment.objects.get(chapa_tx_ref=tx_ref)

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
        }

        response = requests.get(f"https://api.chapa.co/v1/transaction/verify/{tx_ref}", headers=headers)
        data = response.json()

        if data.get('status') == 'success' and data['data']['status'] == 'success':
            payment.status = 'Completed'
        else:
            payment.status = 'Failed'
        payment.save()

        return Response({'status': payment.status}, status=200)

    except Payment.DoesNotExist:
        return Response({'error': 'Invalid transaction reference'}, status=404)    
