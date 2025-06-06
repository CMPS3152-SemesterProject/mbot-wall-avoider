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
    print("\033[94mStarting up.\033[0m")  # Print in blue and reset color
    program.main()


if __name__ == "__main__":
    # Start the connection to the BLE bridge
    if Bluetooth is True:
        multiprocessing.set_start_method("spawn", force=True)
        BluetoothConnector.connect_bridge(device_id=DeviceId)
    startup()
