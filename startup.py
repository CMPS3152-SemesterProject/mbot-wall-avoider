import multiprocessing

import BluetoothConnector
Bluetooth = True
DeviceId = "00:1B:10:FB:FD:6C"


def startup():
    import main as program
    """
    This function is called when the robot first starts up.
    It is intended to be used for any setup or initialization
    that needs to be done before the main loop begins.
    """
    print("Starting up.")
    program.entry_point()


if __name__ == "__main__":
    # Start the connection to the BLE bridge
    if Bluetooth:
        multiprocessing.set_start_method("spawn", force=True)
        BluetoothConnector.connect_bridge(device_id=DeviceId)
    startup()
