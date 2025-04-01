import makeblock

from EncoderController import EncoderController
from makeblock.boards import MeAuriga
from makeblock.modules.rj25 import LineFollower
from makeblock.modules.rj25 import Ultrasonic
from time import sleep


# -------------------------
#   Connect to Me Auriga
# -------------------------
# Fallback to COM4 if not using BLE
makeblock.add_port("COM4")
board = MeAuriga.connect(BLE=True)

# -------------------------
#   Sensor Setup
# -------------------------
# Double-check the physical ports on your robot:
lineFollower = LineFollower(board, port=6)
ultrasonicSensor = Ultrasonic(board, port=7)

# -------------------------
#   Motor / Controller
# -------------------------
control = EncoderController(board, 1, 2)

# -------------------------
#   Global Variables
# -------------------------
lineFollower_color = 'black'  # Default color
distance = 0


# -------------------------
#   Functions
# -------------------------
def get_code(value):
    """
    Get the color of the line follower sensor
    :param value: Raw value from the sensor
    :return: The color of the line follower sensor
    """
    global lineFollower_color
    if int(value) > 0:
        lineFollower_color = 'white'
    else:
        lineFollower_color = 'black'


def get_distance(value):
    """
    Get the distance from the ultrasonic sensor
    :param value: Raw value from the sensor
    :return: Value of the distance
    """
    global distance
    if distance is 400:
        distance = 0
    distance = value

# -------------------------
#   Main Loop
# -------------------------


def main():
    global lineFollower_color
    global ultrasonicSensor
    global distance
    print("Distance: ", distance)
    print("Color: ", lineFollower_color)
    if distance > 15:
        control.push_forward(100)
    else:
        control.stop()


# Entry point
def entry_point():
    while True:
        ultrasonicSensor.read(get_distance)
        lineFollower.read(get_code)
        main()
        sleep(0.05)  # Minimum sleep time for maximum responsiveness
