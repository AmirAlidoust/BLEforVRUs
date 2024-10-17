# Bluetooth Low Energy (BLE) Beacons for supporting Vulnerable Road Users (VRU)

This project is done as part of the master's curriculum of RCSE at TU Ilmenau and focuses on addressing the risk of collisions between cyclists by developing a real-time detection system using Bluetooth Low Energy (BLE) technology.

## Methodology

The BLE bike detection system effectively integrates Python, Django, and RESTful APIs to provide real-time scanning, risk assessment, and visualization of nearby bikes. By leveraging multithreading for concurrent scanning and data visualization, the system offers cyclists timely insights into potential collision risks, enhancing safety and awareness.

## Steps for Django setup and to run server:

Make sure Python is installed on your local machine.

1. **Clone the Repository**

    ```sh
    git clone https://github.com/basit3000/Group-Studies-Project-.git
    ```

2. **Navigate to the Project Directory**

    ```sh
    cd Group-Studies-Project-
    ```

3. **Upgrade pip (Optional but Recommended)**

    ```sh
    python -m pip install --upgrade pip
    ```

4. **Create a Virtual Environment**

    ```sh
    python -m venv venv
    ```

5. **Activate the Virtual Environment**

    - On Windows:

        ```sh
        venv\Scripts\activate
        ```

    - On macOS and Linux:

        ```sh
        source venv/bin/activate
        ```

6. **Install Dependencies**

    ```sh
    pip install -r requirements.txt
    ```

7. **Run the Django Server**

    ```sh
    python lowEnergyBT/manage.py runserver
    ```
