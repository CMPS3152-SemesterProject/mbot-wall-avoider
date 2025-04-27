# mbot-wall-avoider
mbot-wall-avoider

## Overview

This project is an mBot wall-avoider robot using Arduino C++ and the Makeblock C++ Library.

## Setup Instructions

### Prerequisites

1. Install the Arduino IDE from [here](https://www.arduino.cc/en/software).
2. Install the Makeblock library:
   - Open the Arduino IDE.
   - Go to `Sketch` > `Include Library` > `Manage Libraries`.
   - In the Library Manager, search for `Makeblock` and install the latest version.

### Uploading the Code

1. Connect your mBot to your computer using a USB cable.
2. Open the `mbot_wall_avoider.ino` file in the Arduino IDE.
3. Select the correct board and port:
   - Go to `Tools` > `Board` and select `Arduino/Genuino Uno`.
   - Go to `Tools` > `Port` and select the port to which your mBot is connected.
4. Click the `Upload` button to upload the code to your mBot.

## Usage

Once the code is uploaded, your mBot will start avoiding walls using the sensors and motors.

> [!WARNING]
> If using Bluetooth to connect
>
> Ensure to search for your device's ID by running the following in the terminal
```
ble-scan
```

And then placing it in the file `BluetoothConnector/BluetoothConnector.ino`

```cpp
const char* DeviceId = "00:1B:10:FB:A6:7C";  <---- HERE ⚠️
```
