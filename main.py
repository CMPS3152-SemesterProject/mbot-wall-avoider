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
initial_turn = False
lineFollower_color = 'black'  # Default color
distance = 0
distance_left = 0
distance_right = 0
unjam_retries = 0
SPEED = 60
OPTIMISTIC = False
bot_is_facing = "FORWARD"  # Default direction


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
    global distance_left
    if int(value) > 0:
        board.set_tone(300, 500)
        lineFollower_color = 'white'
        # distance_left = 0
    else:
        lineFollower_color = 'black'
        # distance_left = 20


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
    control.sharp_left(speed, int(1058 * (120 / timeout)))


def turn_90_left(speed, is_left):
    global distance_left
    global distance_right
    if int(speed) < 0:
        timeout = (speed * -1)
    else:
        timeout = speed
    control.sharp_left(speed, int(320 * (120 / timeout)))
    if is_left == "left":
        ultrasonicSensor.read(get_distance)
        distance_left = distance
    elif is_left == "right":
        ultrasonicSensor.read(get_distance)
        distance_right = distance


def update_bot_position(position):
    """
    Update the bot's position based on the given direction.
    :param position: The direction to update the bot's position
    """
    global bot_is_facing
    if position == "FORWARD":
        bot_is_facing = "FORWARD"
    elif position == "BACKWARD":
        bot_is_facing = "BACKWARD"
    elif position == "LEFT":
        bot_is_facing = "LEFT"
    elif position == "RIGHT":
        bot_is_facing = "RIGHT"

# -------------------------
#   Main Loop
# -------------------------


def main():
    global lineFollower_color, ultrasonicSensor, distance, SPEED, \
        distance_left, distance_right, unjam_retries, initial_turn
    roll = board.get_roll()

    print(f"Distance: {distance}")
    print(f"Distance Left: {distance_left}")
    print(f"Distance Right: {distance_right}")
    print(f"Color: {lineFollower_color}")
    print(f"Roll: {roll}")

    # if lineFollower_color == 'white' and (distance == 0 or distance == 400):
    #     control.push_forward(SPEED)
    # elif distance_left == 20 and initial_turn is False:
    #     control.push_forward(SPEED)
    #     sleep(1)
    #     control.stop()
    #     turn_90_left(SPEED, "left")
    #     control.move_forward(SPEED, 500)
    #     initial_turn = True
    # If on black line but the robot is tilted significantly => unjam
    if lineFollower_color == 'black' and float(roll) < -30.0:
        print("Detected tilt; attempting to unjam.")
        control.move_backward(int(50 * (unjam_retries + 1)), 500)
        unjam_retries += 1
    elif distance > 15:
        control.push_forward(SPEED)
    else:
        control.stop()
        sleep(0.5)

        # Measure distance to the right
        turn_90_left(speed=(SPEED * -1), is_left="right")
        update_bot_position("RIGHT")
        sleep(0.5)

        # Reset to original position
        turn_90_left(speed=(SPEED * -1), is_left="none")
        sleep(0.5)
        update_bot_position("BACKWARD")

        # Measure distance to the left
        turn_90_left(speed=SPEED, is_left="left")
        update_bot_position("LEFT")
        sleep(0.5)
        print("========================================================")
        print(f"Distance: {distance}")
        print(f"Distance Left: {distance_left}")
        print(f"Distance Right: {distance_right}")
        print(f"Color: {lineFollower_color}")
        print(f"Roll: {roll}")
        # Compare left and right distances to decide the direction
        if distance_left > distance_right:
            if bot_is_facing == "LEFT":
                print("Already facing LEFT, moving forward.")
                control.push_forward(SPEED)
            else:
                print("Turning LEFT (More space to the left)")
                turn_90_left(speed=SPEED, is_left="none")
        elif distance_right > distance_left:
            if bot_is_facing == "RIGHT":
                print("Already facing RIGHT, moving forward.")
                control.push_forward(SPEED)
            else:
                sleep(10)
                print("Turning RIGHT (More space to the right)")
                turn_90_left(speed=(SPEED * -1), is_left="none")
        else:
            print("Distances are equal or unclear, turning around.")
            turn_90_left(SPEED, is_left="none")
            update_bot_position("LEFT")
            sleep(0.05)
            turn_90_left(SPEED, is_left="none")
            update_bot_position("LEFT")

        sleep(0.5)


# Entrypoint
def entry_point():
    board.set_tone(50, 500)
    ultrasonicSensor.read(get_distance)
    lineFollower.read(get_code)
    sleep(3)
    board.set_tone(100, 300)
    while True:
        ultrasonicSensor.read(get_distance)
        lineFollower.read(get_code)
        main()
        sleep(0.05)  # Minimum sleep time for maximum responsiveness
