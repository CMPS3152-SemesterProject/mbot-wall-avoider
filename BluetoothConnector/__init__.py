import subprocess
import os
import multiprocessing


def fork_process(target_func, *args, **kwargs):
    """
    Create a detached process using multiprocessing.
    """
    process = multiprocessing.Process(target=target_func, args=args, kwargs=kwargs)
    process.daemon = True  # Makes the process a daemon process (dies when parent dies)
    process.start()
    print(f"Parent process. PID: {os.getpid()}, Child PID: {process.pid}")
    return process


def child_process(device_id):
    """
    The function to run in the child process.
    """
    print(f"Child process. PID: {os.getpid()}")
    subprocess.run([
        "ble-serial", "-d", device_id,
        "-r", "0000ffe2-0000-1000-8000-00805f9b34fb",
        "-w", "0000ffe3-0000-1000-8000-00805f9b34fb"
    ])


def connect_bridge(device_id):
    """
    Initiate the BLE connection by forking a process to handle the connection.
    """
    process = fork_process(child_process, device_id)
    # Don't call process.join() since we want the child process to be independent
    return process
