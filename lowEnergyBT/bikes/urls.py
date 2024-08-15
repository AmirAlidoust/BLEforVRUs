from django.urls import path
from .views import StartBLECommunication

urlpatterns = [
    path('bikes/start-ble/', StartBLECommunication.as_view(), name='start-ble'),
]
