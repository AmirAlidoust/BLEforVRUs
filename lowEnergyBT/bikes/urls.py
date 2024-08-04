from django.urls import path
from .views import BikeListCreate, ProximityCheck, StartBLECommunication

urlpatterns = [
    path('bikes/', BikeListCreate.as_view(), name='bike-list-create'),
    path('bikes/proximity/', ProximityCheck.as_view(), name='proximity-check'),
    path('bikes/start-ble/', StartBLECommunication.as_view(), name='start-ble'),
]
