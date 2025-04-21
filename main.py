import makeblock

from EncoderController import EncoderController
from makeblock.boards import MeAuriga
from makeblock.modules.rj25 import LineFollower
from makeblock.modules.rj25 import Ultrasonic
from Wall import Wall
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
loop_detection_counter = 1
inside_inner_island = False
SPEED = 60
OPTIMISTIC = False
bot_is_facing = "FORWARD"  # Default direction
memory = ["FORWARD", 13, "LEFT", "FORWARD", 13, "LEFT", "FORWARD", 13, "LEFT", "FORWARD", 13, "LEFT"]  # Note: 13 steps @125ms @SPEED=60 is ~1 ft.
# Checkpoints are the indices of the memory list where the bot has turned
# memory = ["FORWARD"]
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


def print_flush(message):
    """
    Print a message and flush the output buffer.
    :param message: The message to print
    """
    print(message, end="\n", flush=True)


def virtual_step(steps: float, speed: float, base_speed: float = 60, base_step_count: float = 13):
    """
    Calculates the adjusted number of real steps required to cover the same distance
    as base_step_count steps at base_speed.

    Parameters:
        steps (float): Number of virtual STEPS (1 STEP = 13 real steps)
        speed (float): Current speed setting
        base_speed (float): Reference speed (default = 60)
        base_step_count (float): Reference steps at base speed (default = 13)

    Returns:
        float: Number of real steps needed at the given speed
    """
    real_steps = steps * base_step_count  # Convert virtual steps to real steps
    adjusted_steps = real_steps * (base_speed / speed)
    print(f"Virtual step: {steps} -> Real step: {real_steps} -> Adjusted step: {adjusted_steps}", flush=True)
    return adjusted_steps


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


def display_checkpoints():
    """
    Display the checkpoints of the bot.
    """
    global checkpoints
    print("Checkpoints:", flush=True)
    for i in range(len(checkpoints)):
        print(f"  {i}: {checkpoints[i]}", flush=True)
    print("End of Checkpoints", flush=True)


def play_memory(checkpoint_n=0):
    """
    Play the memory of the bot.
    NOTICE: Ensure to run `control.stop()` immediately after running.
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
                        sleep(0.125)
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
                if i + 1 < len(memory) and isinstance(memory[i + 1], int):
                    for _ in range(memory[i + 1]):
                        control.push_backward(SPEED)
                        sleep(0.125)
                    print(f"    Executed BACKWARD {memory[i + 1]} times", flush=True)
                    i += 2
                    continue
                else:
                    print("    ERROR: BACKWARD not followed by an integer", flush=True)
            else:
                print(f"    WARNING: Unknown command '{item}'", flush=True)
        elif isinstance(item, int):
            print("    ERROR: Unexpected integer without preceding FORWARD", flush=True)
        i += 1
        sleep(0.125)

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
    if len(memory) > 0:
        # Check if n is within the bounds of the checkpoints
        if n > len(checkpoints):
            raise ValueError("n is out of bounds for rollback.")
        # Rollback the memory by n checkpoints
        for _ in range(n):
            if len(memory) > 0:
                memory.pop()
                if len(memory) > 0 and (isinstance(memory[-1], str) and memory[-1] == "FORWARD"):
                    # Remove the last string command
                    memory.pop()
            else:
                break
        print(f"Rolled back {n} checkpoints", flush=True)
    else:
        print("No memory to rollback", flush=True)

# -------------------------
#   Wall Avoidance
# -------------------------


def avoid_wall(counter):
    control.stop()  # stop when front wall is hit or too close
    control.move_backward(50, 300)  # Move back a bit
    # Turn left 90 degrees, might need some tweaking
    turn_90_left(SPEED, "left")
    counter += 1

# -------------------------
#   Main Loop
# -------------------------


def main():
    global lineFollower_color, ultrasonicSensor, distance, SPEED, \
        distance_left, distance_right, unjam_retries, initial_turn, memory, \
        loop_detection_counter, inside_inner_island
    roll = board.get_roll()

    # If on black line but the robot is tilted significantly => unjam
    if lineFollower_color == 'black' and float(roll) < -30.0:
        print("Detected tilt; attempting to unjam.")
        control.move_backward(int(50 * (unjam_retries + 1)), 500)
        unjam_retries += 1
    elif lineFollower_color == 'white' and inside_inner_island is True:
        print_flush("Inside inner island. Stopping Motors.")
        control.stop()
        sleep(4)
        print_flush("Replaying memory in reverse.")
        # todo: Ideally, have another argument to play memory in reverse
        # play_memory(checkpoint_n=0)
        # But for now we will just exit
        exit(1)  # Placeholder
    elif lineFollower_color == 'white' and inside_inner_island is False:
        # Check if memory is not empty and last element is a string
        if len(memory) > 0 and isinstance(memory[-1], str):
            memory.append("FORWARD")
            memory.append(0)
        print_flush("Wall encountered. Making right turn.")
        avoid_wall(loop_detection_counter)
        # Reset the unjam retries
        unjam_retries = 0
        if loop_detection_counter == 4 and inside_inner_island is False:
            print_flush("Loop detected. Adjusting.")
            print_flush("Making 180deg turn.")
            turn_90_left(SPEED, "left")
            turn_90_left(SPEED, "left")
            inside_inner_island = True
            # Ideally, put a function below. But for now, just a placeholder.
    if distance_left > 11:
        print_flush("Left distance is too far. Adjusting.")
        # Slight right turn
        control.encoder_left.run(22)
        control.encoder_right.run(-13)
        sleep(1.25)
    if distance_left < 7:
        print_flush("Left distance is too close. Adjusting.")
        # Slight left turn
        control.encoder_left.run(13)
        control.encoder_right.run(-16)
    if 12 > distance_left > 7:
        print_flush("Left distance is just right. Continuing.")
        # Move forward
        control.push_forward(SPEED)
        # If memory has at least two elements and the second last is a string
        if len(memory) > 1 and isinstance(memory[-2], str) and isinstance(memory[-1], int):
            if len(memory) < 0:
                memory[-1] += 1
        # else:
        #     control.stop()
        #     print("Current memory")
        #     display_memory()
        #     print("Current checkpoints")
        #     display_checkpoints()
        #     memory_rollback_by_checkpoint_n(4)
        #     sleep(5)
        #     play_memory()
        #     control.stop()
        #     exit(0)
        else:
            memory.append("FORWARD")
    sleep(0.5)  # Appropriate clock time for the bot to move


# Entrypoint
def entry_point():
    global distance, lineFollower_color, \
        loop_detection_counter, inside_inner_island
    board.set_tone(50, 500)
    get_distance()
    lineFollower.read(get_code)
    sleep(3)
    board.set_tone(100, 300)
    while True:
        lineFollower.read(get_code)
        main()
        sleep(0.05)  # Minimum sleep time for maximum responsiveness
        print("\r" + " " * 50, end=" ")  # Clears the line
        # Add color to the distance and line color, and different colors to their values
        print(f"\r\033[94mDistance:\033[0m \033[92m{distance}\033[0m "
              f" | \033[94mLine color:\033[0m \033[92m{lineFollower_color}\033[0m "
              f"| \033[94mCounter :\033[0m \033[92m{loop_detection_counter}\033[0m "
              f" | \033[94mInside Island:\033[0m \033[92m{inside_inner_island}\033[0m", end="\n", flush=True)
