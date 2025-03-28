# mbot-wall-avoider
mbot-wall-avoider


> [!WARNING]
> If using Bluetooth to connect
>
> Ensure to search for your device's ID by running the following in the terminal
```
ble-scan
```

And then placing it in the file `startup.py`

```python
if __name__ == "__main__":
    # Start the connection to the BLE bridge
    multiprocessing.set_start_method("spawn", force=True)
    BluetoothConnector.connect_bridge("00:1B:10:FB:A6:7C")     <---- HERE ⚠️
    startup()
```
