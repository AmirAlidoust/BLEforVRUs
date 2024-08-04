import asyncio
import requests
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Bike
from .serializers import BikeSerializer
from .utils import haversine_distance
from bleak import BleakScanner, BleakClient

# Fetch the current GPS coordinates from http://ip-api.com
def fetch_current_gps():
    response = requests.get("http://ip-api.com/json")
    data = response.json()
    return data['lat'], data['lon']

# Send location data to another bike via BLE
async def send_location(client, characteristic_uuid, location_data):
    await client.write_gatt_char(characteristic_uuid, location_data.encode(), response=True)

# Read location data from another bike via BLE
async def read_location(client, characteristic_uuid):
    data = await client.read_gatt_char(characteristic_uuid)
    return data.decode().split(',')

# Main BLE communication function
async def ble_communication():
    current_lat, current_lon = fetch_current_gps()
    print(f"Current location: Latitude {current_lat}, Longitude {current_lon}")

    devices = await BleakScanner.discover(timeout=10)
    print(f"Discovered devices: {devices}")

    for device in devices:
        print(f"Processing device: {device}")
        try:
            # Connect to the device using context manager
            async with BleakClient(device.address) as client:
                print(f"Connected to device: {device.address}")
                services = await client.get_services()

                for service in services:
                    service_uuid = service.uuid
                    print(f"Service UUID: {service_uuid}")

                    for characteristic in service.characteristics:
                        characteristic_uuid = characteristic.uuid
                        print(f"Characteristic UUID: {characteristic_uuid}")

                        await send_location(client, characteristic_uuid, f"{current_lat},{current_lon}")
                        other_lat, other_lon = await read_location(client, characteristic_uuid)
                        other_lat, other_lon = float(other_lat), float(other_lon)

                        distance = haversine_distance(current_lat, current_lon, other_lat, other_lon)
                        print(f"Distance to other bike: {distance} meters")

                        if distance < 50:
                            print("Warning: Another bike is getting close to you!")
                            break
                    break
        except Exception as e:
            print(f"Error processing device {device.address}: {e}")
            continue  # Skip to the next device if an error occurs

class BikeListCreate(generics.ListCreateAPIView):
    queryset = Bike.objects.all()
    serializer_class = BikeSerializer

class ProximityCheck(APIView):
    def post(self, request):
        try:
            latitude = request.data['latitude']
            longitude = request.data['longitude']
            threshold = request.data.get('threshold', 50)  # default threshold 50 meters

            nearby_bikes = []
            for bike in Bike.objects.all():
                distance = bike.distance_to(latitude, longitude)
                if distance < threshold:
                    nearby_bikes.append(BikeSerializer(bike).data)

            return Response(nearby_bikes, status=status.HTTP_200_OK)
        except KeyError:
            return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

# Endpoint to trigger BLE communication
class StartBLECommunication(APIView):
    def get(self, request):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(ble_communication())
            return JsonResponse({"status": "BLE communication started"})
        except Exception as e:
            # Log the exception for debugging
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
