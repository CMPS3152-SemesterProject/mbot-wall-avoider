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
unjam_retries = 0
SPEED = 60
OPTIMISTIC = False
bot_is_facing = "FORWARD"  # Default direction
memory = ["FORWARD", 0]
# Checkpoints are the indices of the memory list where the bot has turned
checkpoints = [i + 1 for i in range(len(memory)) if memory[i] == "FORWARD"]

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


def play_memory(checkpoint_n=0):
    """
    Play the memory of the bot.
    """
    global memory
    i = 0
    len_memory = len(memory)
    if checkpoint_n > 0:
        # Reverse offset: going back from the end of the memory
        len_memory = len(checkpoints) - 1 - checkpoint_n
        if 0 <= len_memory < len(checkpoints):
            len_memory = checkpoints[len_memory] + 1
            print(f"Playing memory from checkpoint {checkpoint_n} (index {len_memory})", flush=True)
            # Pop off everything after the checkpoint
            while len(memory) > len_memory:
                memory.pop()
        else:
            raise ValueError("checkpoint_N is out of bounds for reverse indexing.")
    while i < len_memory:
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

    if checkpoint_n != 0:
        print("End of Checkpoint", flush=True)
    else:
        print("End of Memory", flush=True)


def memory_rollback_by_checkpoint_n(n):
    """
    Rollback the memory by n checkpoints.
    :param n: Number of checkpoints to rollback
    """
    global memory
    if len(memory) > 0 and isinstance(memory[-1], int):
        # Play the last n checkpoints
        play_memory(n)
        memory.pop()
        print(f"Rolled back {n} checkpoints", flush=True)
    else:
        print("No memory to rollback", flush=True)

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
    elif lineFollower_color == 'white':
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
        # Code in here
        sleep(0.5)


# Entrypoint
def entry_point():
    board.set_tone(50, 500)
    get_distance()
    lineFollower.read(get_code)
    sleep(3)
    board.set_tone(100, 300)
    while True:
        lineFollower.read(get_code)
        main()
        sleep(0.05)  # Minimum sleep time for maximum responsiveness
