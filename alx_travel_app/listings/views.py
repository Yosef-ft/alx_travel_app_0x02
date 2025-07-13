from django.shortcuts import render
from .serializers import ListingSerializer, BookingSerializer
from .models import Listing, Booking
from rest_framework.viewsets import ModelViewSet


class ListingViewSet(ModelViewSet):
    serializer_class = ListingSerializer
    queryset = Listing.objects.all()


class BookingViewSet(ModelViewSet):
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()
