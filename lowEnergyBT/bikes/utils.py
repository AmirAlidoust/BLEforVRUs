def calculate_distance(rssi, tx_power=-59, n=2):
    if rssi == 0:
        return -1.0  # if we cannot determine distance, return -1.
    ratio = rssi / tx_power
    if ratio < 1.0:
        return ratio ** 10
    else:
        return 10 ** ((tx_power - rssi) / (10 * n))
