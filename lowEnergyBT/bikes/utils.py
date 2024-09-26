import matplotlib.pyplot as plt
import numpy as np
import math

def calculate_distance(rssi):
    tx_power = -59  # Assuming Tx Power
    n = 2  # Path-loss exponent for the environment
    if rssi[-1] == 0:
        return -1.0  # if we cannot determine distance, return -1.
    
    ratio = rssi[-1] / tx_power
    if ratio < 1.0:
        return math.pow(ratio, 10)
    else:
        return math.pow(10, (tx_power - rssi[-1]) / (10 * n))

def calculate_time_intervals(speed, distance, acceleration, deceleration, vehicle_length, lane_width, pass_speed):
    # Time to reach the point with acceleration
    if acceleration > 0:
        t_min = (-speed + math.sqrt(speed**2 + 2 * acceleration * distance)) / acceleration
    else:
        t_min = float('inf')  # If no acceleration, the bike won't speed up

    # Time to pass the bike or stop
    t_pass = (vehicle_length + lane_width) / pass_speed

    # Time to stop or pass (if stopping is impossible)
    if speed**2 + 2 * deceleration * distance >= 0:
        t_max = (-speed + math.sqrt(speed**2 + 2 * deceleration * distance)) / deceleration + t_pass
    else:
        t_max = float('inf')  # If stopping is impossible, it keeps moving forward
    
    return t_min, t_max

def classify_risk(tmin_bike1, tmax_bike1, tmin_bike2, tmax_bike2):
    if tmin_bike1 > tmax_bike2 or tmin_bike2 > tmax_bike1:
        return "NO-CRASH"  # No time overlap, no risk
    elif tmax_bike1 == float('inf') and tmax_bike2 == float('inf'):
        return "SAFE"  # Both bikes can stop safely
    elif tmax_bike1 == float('inf') or tmax_bike2 == float('inf'):
        return "ATTENTION"  # One bike can stop, but risk still exists
    else:
        return "CRITICAL"  # High chance of collision due to overlapping intervals


def plot_bikes(bike_data):
    # Plot bikes around the central bike (our bike at 0,0), grouping them by risk category.
    
    fig, ax = plt.subplots(figsize=(10, 10))

    # Colors for different risk levels
    risk_colors = {
        "CRITICAL": 'red',
        "ATTENTION": 'orange',
        "SAFE": 'green',
        "NO-CRASH": 'gray'
    }

    # Place the user's bike at the center (origin)
    ax.plot(0, 0, 'bo', markersize=12, label="My Bike (0,0)")

    # Separate bikes by risk category (use 'classification' instead of 'risk')
    for risk_level in risk_colors.keys():
        risk_bikes = [bike for bike in bike_data if bike['classification'] == risk_level]
        x_positions = []
        y_positions = []
        
        # Calculate positions for bikes based on their distance
        for bike in risk_bikes:
            try:
                # Convert the 'distance' from "X meters" to float
                distance = float(bike['distance'].split()[0])  # Extract numeric value
                angle = np.random.uniform(0, 2 * np.pi)  # Random angle
                x_pos = distance * np.cos(angle)
                y_pos = distance * np.sin(angle)
                x_positions.append(x_pos)
                y_positions.append(y_pos)
            except Exception as e:
                print(f"Error processing bike distance: {bike['distance']}. Error: {e}")
                continue
        
        # Plot bikes in this risk category
        ax.plot(x_positions, y_positions, 'o', markersize=6, color=risk_colors[risk_level], label=f"{risk_level}")

    # Set plot properties
    ax.set_xlabel("X Position (meters)")
    ax.set_ylabel("Y Position (meters)")
    ax.set_title("Bike Distances Around My Bike (at 0,0)")
    
    # Adjust axes limits based on the maximum distance
    if bike_data:
        max_distance = max(float(bike['distance'].split()[0]) for bike in bike_data)
        ax.set_xlim(-max_distance - 10, max_distance + 10)
        ax.set_ylim(-max_distance - 10, max_distance + 10)

    # Move the legend outside of the plot
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='medium')

    # Add grid, and equal aspect ratio for clarity
    ax.grid(True)
    ax.set_aspect('equal', adjustable='box')

    # Tighter layout to avoid unnecessary white space
    plt.tight_layout()
    
    # Return the figure and axes objects
    return fig, ax
