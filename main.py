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
LINEFOLLOWER_PORT = 6
ULTRASONIC_PORT = 7
# Double-check the physical ports on your robot:
lineFollower = LineFollower(board, port=LINEFOLLOWER_PORT)
ultrasonicSensor = Ultrasonic(board, port=ULTRASONIC_PORT)
DISTANCE_THRESHOLD = 15

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
memory = ["FORWARD", 0, "FORWARD", 58, "RIGHT", "FORWARD", 20, "RIGHT", "FORWARD", 13, "LEFT", "FORWARD", 8, "LEFT", "FORWARD", 103]


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


def get_distance():
    """
    Get the distance from the ultrasonic sensor
    :return: Value of the distance
    """
    global distance
    value = ultrasonicSensor.get_distance(port=ULTRASONIC_PORT)
    if value == 400:
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
    get_distance()  # Get ultrasonic distance
    if is_left == "left":
        distance_left = distance
    if is_left == "right":
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


def display_memory():
    """
    Display the memory of the bot.
    """
    global memory
    print("Memory:", flush=True)
    for i in range(len(memory)):
        if isinstance(memory[i], str):
            print(f"  {i}: {memory[i]}", flush=True)
        else:
            print(f"  {i}: {memory[i]}", flush=True)
    print("End of Memory", flush=True)


def play_memory():
    """
    Play the memory of the bot.
    """
    global memory
    i = 0
    while i < len(memory):
        item = memory[i]
        print(f"  {i}: {item}", flush=True)

        if isinstance(item, str):
            if item == "FORWARD":
                if i + 1 < len(memory) and isinstance(memory[i + 1], int):
                    for _ in range(memory[i + 1]):
                        control.push_forward(SPEED)
                    print(f"    Executed FORWARD {memory[i + 1]} times", flush=True)
                    i += 2
                    continue
                else:
                    print("    ERROR: FORWARD not followed by an integer", flush=True)
            elif item == "LEFT":
                turn_90_left(speed=SPEED, is_left="none")
            elif item == "RIGHT":
                turn_90_left(speed=(SPEED * -1), is_left="none")
            elif item == "BACKWARD":
                control.move_backward(SPEED, 500)
            else:
                print(f"    WARNING: Unknown command '{item}'", flush=True)
        elif isinstance(item, int):
            print("    ERROR: Unexpected integer without preceding FORWARD", flush=True)

        i += 1

    print("End of Memory", flush=True)


# -------------------------
#   Main Loop
# -------------------------


def main():
    global lineFollower_color, ultrasonicSensor, distance, SPEED, \
        distance_left, distance_right, unjam_retries, initial_turn, memory
    roll = board.get_roll()

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
    elif distance > DISTANCE_THRESHOLD:
        control.push_forward(SPEED)
        # Check if memory is not empty and last element is a string
        if len(memory) > 0 and isinstance(memory[-1], str):
            memory.append("FORWARD")
            memory.append(0)
        # If memory has at least two elements and the second last is a string
        elif len(memory) > 1 and isinstance(memory[-2], str) and isinstance(memory[-1], int):
            memory[-1] += 1
        else:
            memory.append("FORWARD")
    else:
        control.stop()
        sleep(0.5)

        # Measure distance to the right
        turn_90_left(speed=(SPEED * -1), is_left="right")
        update_bot_position("RIGHT")
        sleep(0.5)

        print("RIGHT=======================================================")
        print(f"Distance: {distance}")
        print(f"Distance Left: {distance_left}")
        print(f"Distance Right: {distance_right}")
        print(f"Color: {lineFollower_color}")
        print(f"Roll: {roll}")

        # Reset to original position
        turn_90_left(speed=SPEED, is_left="none")
        update_bot_position("FORWARD")
        sleep(0.5)

        # Measure distance to the left
        turn_90_left(speed=SPEED, is_left="left")
        update_bot_position("LEFT")
        sleep(0.5)

        # Reset to original position
        turn_90_left(speed=(SPEED * -1), is_left="none")
        update_bot_position("FORWARD")
        sleep(0.5)

        print("FINAL=======================================================")
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
                # Check if memory is not empty and last element is an integer
                if len(memory) > 0 and isinstance(memory[-1], int):
                    memory.append("LEFT")
            else:
                print("Turning LEFT (More space to the left)")
                turn_90_left(speed=SPEED, is_left="none")
                # Check if memory is not empty and last element is an integer
                if len(memory) > 0 and isinstance(memory[-1], int):
                    memory.append("LEFT")
        elif distance_right > distance_left:
            if bot_is_facing == "RIGHT":
                print("Already facing RIGHT, moving forward.")
                control.push_forward(SPEED)
                # Check if memory is not empty and last element is an integer
                if len(memory) > 0 and isinstance(memory[-1], int):
                    memory.append("RIGHT")
            else:
                print("Turning RIGHT (More space to the right)")
                turn_90_left(speed=(SPEED * -1), is_left="none")
                # Check if memory is not empty and last element is an integer
                if len(memory) > 0 and isinstance(memory[-1], int):
                    memory.append("RIGHT")
        else:
            print("Distances are equal or unclear, turning around.")
            turn_90_left(SPEED, is_left="none")
            update_bot_position("LEFT")
            sleep(0.05)
            turn_90_left(SPEED, is_left="none")
            update_bot_position("LEFT")
            # Check if memory is not empty and last element is an integer
            if len(memory) > 0 and isinstance(memory[-1], int):
                memory.append("BACKWARD")

        sleep(0.5)


# Entrypoint
def entry_point():
    board.set_tone(50, 500)
    get_distance()
    lineFollower.read(get_code)
    sleep(3)
    board.set_tone(100, 300)
    while True:
        play_memory()
        exit(0)
        get_distance()
        lineFollower.read(get_code)
        main()
        sleep(0.05)  # Minimum sleep time for maximum responsiveness
