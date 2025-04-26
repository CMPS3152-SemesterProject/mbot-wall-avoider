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
Bluetooth = True
DeviceId = "00:1B:10:FB:A6:7C"  <---- HERE (Line 5) ⚠️
```
