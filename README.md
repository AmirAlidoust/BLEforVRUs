# BLEforVRUs
 Bluetooth Low Energy (BLE) Beacons for supporting Vulnerable Road Users (VRU)

# Steps for Django setup and to run server:

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
