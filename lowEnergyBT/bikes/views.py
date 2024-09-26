import time
import threading
import asyncio
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bleak import BleakScanner
from .utils import calculate_distance, calculate_time_intervals, classify_risk, plot_bikes
import matplotlib.pyplot as plt

# Global shared variable to pass data between threads
nearby_bikes_data = []

ACCELERATION = 2.5  # m/s^2
DECELERATION = -4.5  # m/s^2
VEHICLE_LENGTH = 1.8  # meters, for a bike
LANE_WIDTH = 3.0  # meters, assume bike lane width
PASS_SPEED = 5.0  # m/s, assume speed while passing

async def scan_for_devices():
    devices = []

    def callback(device, advertisement_data):
        devices.append({
            "address": device.address,
            "rssi": advertisement_data.rssi
        })

    scanner = BleakScanner(detection_callback=callback)
    await scanner.start()
    await asyncio.sleep(5)  # Scan for 5 seconds
    await scanner.stop()
    return devices

def ble_scanning_thread():
    global nearby_bikes_data
    recognized_devices = {}
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        devices = loop.run_until_complete(scan_for_devices())
        print(f"Discovered devices: {devices}")

        nearby_bikes = []

        unique_devices = {device["address"]: device for device in devices}.values()

        for device in unique_devices:
            try:
                device_address = device["address"]
                rssi = device["rssi"]
                print(f"recognized devices are: {recognized_devices}")

                rssi_values = [rssi]
                distance = calculate_distance(rssi_values)

                recognized_devices[device_address] = distance

                v0 = 15  # m/s

                # Fetching time intervals for the current bike
                tmin_bike, tmax_bike = calculate_time_intervals(v0, distance, ACCELERATION, DECELERATION, VEHICLE_LENGTH, LANE_WIDTH, PASS_SPEED)
                
                 # Compare with the other bikes in recognized_devices for potential crashes
                for other_bike in recognized_devices.values():
                    # Assuming the same speed and deceleration for the other bike
                    tmin_other_bike, tmax_other_bike = calculate_time_intervals(v0, other_bike, ACCELERATION, DECELERATION, VEHICLE_LENGTH, LANE_WIDTH, PASS_SPEED)

                    # Classify risk based on time overlap
                    risk = classify_risk(tmin_bike, tmax_bike, tmin_other_bike, tmax_other_bike)

                    print(f"Risk classification between my bike and {other_bike}: {risk}")

                # Append bike information into nearby_bikes list for JSON response
                nearby_bikes.append({
                    "device_address": device_address,
                    "distance": f"{distance:.2f} meters",
                    "classification": risk
                })

                # Update the recognized_devices dictionary with new data
                recognized_devices[device_address] = distance

            except Exception as e:
                print(f"Error processing device {device_address}: {e}")
                continue

        # Update the shared data for plotting and response
        nearby_bikes_data = nearby_bikes

        # Print or prepare the JSON output for debugging
        print(f"Nearby bikes data: {nearby_bikes}")

        # Wait before the next scan
        time.sleep(5)

def plot_and_save_thread():
    global nearby_bikes_data

    while True:
        if nearby_bikes_data:
            # Create a unique filename using the timestamp
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f'bike_plot_{timestamp}.png'

            fig, ax = plot_bikes(nearby_bikes_data)

            fig.savefig(filename)
            plt.close(fig)

            print(f"Plot saved as {filename}")

        time.sleep(10)

class StartBLECommunication(APIView):
    def get(self, request):
        print("GET request received to start BLE communication")

        try:
            scanning_thread = threading.Thread(target=ble_scanning_thread)
            scanning_thread.daemon = True
            scanning_thread.start()

            time.sleep(12)

            plotting_thread = threading.Thread(target=plot_and_save_thread)
            plotting_thread.daemon = True
            plotting_thread.start()

            return JsonResponse({
                "status": "BLE communication started",
                "nearby_bikes": nearby_bikes_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
