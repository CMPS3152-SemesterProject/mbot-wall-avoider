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
distance_left = 0
distance_right = 0
SPEED = 130
OPTIMISTIC = False


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
    global distance_right
    if int(value) > 0:
        lineFollower_color = 'white'
        distance_right = 20
    else:
        lineFollower_color = 'black'
        distance_right = 0


def get_distance(value):
    """
    Get the distance from the ultrasonic sensor
    :param value: Raw value from the sensor
    :return: Value of the distance
    """
    global distance
    if distance == 400:
        if OPTIMISTIC:  # If the distance is 400, we are searching optimistically
            distance = value
        else:
            distance = 0
    else:
        distance = value

# -------------------------
#   Prototype Functions
# -------------------------


def turn_360(speed):
    if int(speed) < 0:
        timeout = (speed * -1)
    else:
        timeout = speed
    control.sharp_left(speed, int(2000 * (120 / timeout)))


def turn_180_left(speed, is_left):
    global distance_left
    global distance_right
    if int(speed) < 0:
        timeout = (speed * -1)
    else:
        timeout = speed
    control.sharp_left(speed, int(330 * (120 / timeout)))
    if is_left == "left":
        sleep(1)
        distance_left = distance
    elif is_left == "right":
        sleep(1)
        distance_right = distance

# -------------------------
#   Main Loop
# -------------------------


def main():
    global lineFollower_color
    global ultrasonicSensor
    global distance
    global SPEED

    print("Distance: ", distance)
    print("Distance Left: ", distance_left)
    print("Distance Right: ", distance_right)
    print("Color: ", lineFollower_color)
    if distance > 15:
        control.push_forward(SPEED)
    else:
        control.stop()
        sleep(0.5)
        # Gauge the distance to the left
        turn_180_left(speed=SPEED, is_left="left")
        # Reset the bot position
        turn_180_left(speed=(SPEED * -1), is_left="none")
        # Gauge the distance to the right
        turn_180_left(speed=(SPEED * -1), is_left="right")
        sleep(0.5)


# Entrypoint
def entry_point():
    while True:
        ultrasonicSensor.read(get_distance)
        lineFollower.read(get_code)
        main()
        sleep(0.05)  # Minimum sleep time for maximum responsiveness
