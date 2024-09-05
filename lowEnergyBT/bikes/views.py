import time
import threading
import asyncio
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bleak import BleakScanner
from .utils import calculate_distance, calculate_braking_distance, classify_risk, plot_bikes
import matplotlib.pyplot as plt
import time

# Global shared variable to pass data between threads
nearby_bikes_data = []

# Assume some constant vehicle properties
ACCELERATION = 2.5  # m/s^2
DECELERATION = -4.5  # m/s^2
VEHICLE_LENGTH = 1.8  # meters, for a bike
LANE_WIDTH = 3.0  # meters, assume bike lane width
PASS_SPEED = 5.0  # m/s, assume speed while passing

# BLE scanning function in a separate thread
async def scan_for_devices():
    devices = []

    def callback(device, advertisement_data):
        devices.append({
            "address": device.address,
            "name": device.name,
            "rssi": advertisement_data.rssi
        })
    
    # Use detection_callback in the constructor
    scanner = BleakScanner(detection_callback=callback)
    await scanner.start()
    await asyncio.sleep(10)  # Scan for 10 seconds
    await scanner.stop()
    return devices

def ble_scanning_thread():
    """Thread responsible for BLE scanning."""
    global nearby_bikes_data
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        devices = loop.run_until_complete(scan_for_devices())
        print(f"Discovered devices: {devices}")

        # Reset nearby_bikes_data for each scan
        nearby_bikes = []

        # Define an arbitrary starting position for the first bike
        bike_position = 0

        for device in devices:
            try:
                rssi = device["rssi"]
                device_address = device["address"]

                # Estimate distance using RSSI
                distance = calculate_distance(rssi)
                print(f"Estimated distance to other bike: {distance} meters")

                # Assume both bikes have the same initial speed
                v0 = 10  # Speed of bike in m/s

                # Calculate braking distances
                braking_distance = calculate_braking_distance(v0, DECELERATION)

                #print(f"Braking distance for Bike: {braking_distance} meters")

                # Classify risk of collision
                risk = classify_risk(distance, braking_distance, braking_distance)

                print(f"Risk classification for bike: {risk}")

                # Append bike information
                nearby_bikes.append({
                    "device": device_address,
                    "position": bike_position,
                    "distance": distance,
                    "braking_distance": braking_distance,
                    "risk": risk
                })

            except Exception as e:
                print(f"Error processing device {device['address']}: {e}")
                continue
        
        # Update the shared data for plotting
        nearby_bikes_data = nearby_bikes

        # Wait before the next scan
        time.sleep(5)

# Plotting function in a separate thread
def plot_and_save_thread():
    """Thread responsible for plotting and saving bike data."""
    global nearby_bikes_data

    while True:
        if nearby_bikes_data:
            # Create a unique filename using the timestamp
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f'bike_plot_{timestamp}.png'

            # Plot all bikes and their distances
            fig, ax = plot_bikes(nearby_bikes_data)

            # Save the plot to a file with the unique filename
            fig.savefig(filename)
            plt.close(fig)  # Close the plot to free up memory

            print(f"Plot saved as {filename}")

        # Wait before checking for new data
        time.sleep(10)

# APIView to start the BLE communication and plotting threads
class StartBLECommunication(APIView):
    def get(self, request):
        print("GET request received to start BLE communication")

        try:
            # Start the BLE scanning thread
            scanning_thread = threading.Thread(target=ble_scanning_thread)
            scanning_thread.daemon = True
            scanning_thread.start()

            # Start the plotting thread
            plotting_thread = threading.Thread(target=plot_and_save_thread)
            plotting_thread.daemon = True
            plotting_thread.start()

            return JsonResponse({
                "status": "BLE communication and plotting started"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
