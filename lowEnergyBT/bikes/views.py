import asyncio
import requests
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Bike
from bleak import BleakScanner
from .utils import calculate_distance

# Scan for BLE devices and store RSSI values
async def scan_for_devices():
    devices = []
    async def callback(device, advertisement_data):
        devices.append({
            "address": device.address,
            "name": device.name,
            "rssi": device.rssi
        })
    
    scanner = BleakScanner()
    scanner.register_detection_callback(callback)
    await scanner.start()
    await asyncio.sleep(5)  # Scan for 5 seconds
    await scanner.stop()
    return devices

# Function to save the device data into the database
def save_bike_data(device_address, distance):
    bike, created = Bike.objects.get_or_create(
        device_address=device_address,
        defaults={'distance': distance}
    )
    if not created:
        bike.distance = distance
        bike.save()

# Main BLE communication function
async def ble_communication():
    devices = await scan_for_devices()
    print(f"Discovered devices: {devices}")

    nearby_bikes = []

    for device in devices:
        print(f"Processing device: {device}")
        try:
            rssi = device["rssi"]

            # Estimate distance using RSSI
            tx_power = -59  # Assuming a Tx Power, this value should be adjusted based on the actual Tx Power of the device
            n = 2  # Path-loss exponent, this can be adjusted based on the environment
            distance = calculate_distance(rssi, tx_power, n)
            print(f"Estimated distance to other bike: {distance} meters")

            if distance < 30:
                print("Warning: Another bike is getting close to you!")
                nearby_bikes.append({
                    "device": device["address"],
                    "distance": distance
                })
                save_bike_data(device["address"], distance)
        except Exception as e:
            print(f"Error processing device {device['address']}: {e}")
            continue

    return nearby_bikes

class StartBLECommunication(APIView):
    def get(self, request):
        print("GET request received")
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            nearby_bikes = loop.run_until_complete(ble_communication())
            print(f"Nearby bikes: {nearby_bikes}")

            return JsonResponse({
                "status": "BLE communication completed",
                "nearby_bikes": nearby_bikes
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error during BLE communication: {e}")
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
