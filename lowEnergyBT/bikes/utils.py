import matplotlib.pyplot as plt
import numpy as np

def calculate_distance(rssi):
    tx_power = -59  # Assuming Tx Power
    n = 2  # Path-loss exponent for the environment
    if rssi == 0:
        return -1.0  # if we cannot determine distance, return -1.
    ratio = rssi / tx_power
    if ratio < 1.0:
        return ratio ** 10
    else:
        return 10 ** ((tx_power - rssi) / (10 * n))


def calculate_braking_distance(speed, deceleration):
    """Calculate braking distance using speed and deceleration."""
    return (speed ** 2) / (2 * abs(deceleration))

def calculate_time_intervals(speed, distance, acceleration, deceleration, vehicle_length, lane_width, pass_speed):
    """Calculate time intervals for possible collision based on speed, distance, and braking factors."""
    # Time to stop
    t_stop = abs(speed / deceleration)
    
    # Time to pass, assuming overtaking situation
    t_pass = (distance - vehicle_length) / pass_speed if distance > vehicle_length else 0
    
    # Minimum and maximum times for possible interaction
    tmin = min(t_stop, t_pass)
    tmax = max(t_stop, t_pass)
    
    return tmin, tmax

def classify_risk(distance, braking_distance_1, braking_distance_2):
    """Classify risk based on the braking distances and the actual distance between bikes."""
    total_braking_distance = braking_distance_1 + braking_distance_2

    if distance <= total_braking_distance:
        return "CRITICAL"
    elif distance <= total_braking_distance * 2:
        return "ATTENTION"
    else:
        return "SAFE"


def plot_bikes(bike_data):
    """
    Plot bikes around the central bike (our bike at 0,0), grouping them by risk category.
    
    bike_data: List of dictionaries containing 'device', 'distance', 'braking_distance', 'risk', and 'position'.
    """
    fig, ax = plt.subplots(figsize=(10, 10))

    # Colors for different risk levels
    risk_colors = {
        "CRITICAL": 'red',
        "ATTENTION": 'orange',
        "SAFE": 'green'
    }

    # Place the user's bike at the center (origin)
    ax.plot(0, 0, 'bo', markersize=12, label="My Bike (0,0)")

    # Separate bikes by risk category
    for risk_level in risk_colors.keys():
        risk_bikes = [bike for bike in bike_data if bike['risk'] == risk_level]
        x_positions = []
        y_positions = []
        
        # Calculate positions for bikes based on their distance
        for bike in risk_bikes:
            distance = bike['distance']
            angle = np.random.uniform(0, 2 * np.pi)  # Random angle
            x_pos = distance * np.cos(angle)
            y_pos = distance * np.sin(angle)
            x_positions.append(x_pos)
            y_positions.append(y_pos)
        
        # Plot bikes in this risk category
        ax.plot(x_positions, y_positions, 'o', markersize=6, color=risk_colors[risk_level], label=f"{risk_level} Bikes")

    # Set plot properties
    ax.set_xlabel("X Position (meters)")
    ax.set_ylabel("Y Position (meters)")
    ax.set_title("Bike Distances Around My Bike (at 0,0)")
    
    # Adjust axes limits based on the maximum distance
    max_distance = max(bike['distance'] for bike in bike_data)
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