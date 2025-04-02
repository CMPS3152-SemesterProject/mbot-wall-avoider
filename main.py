import makeblock
import matplotlib.pyplot as plt
import matplotlib.patches as patches

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
unjam_retries = 0
SPEED = 60
OPTIMISTIC = True
# Dictionary to store the map
maze_map = {}  # Key: (x, y) tuple, Value: Cell state (1 = open, -1 = wall, 0 = unexplored)
# Initialize starting point
current_position = (0, 0)
maze_map[current_position] = 1  # Starting point is marked as open


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
        board.set_tone(300, 500)
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
    control.sharp_left(speed, int(1058 * (120 / timeout)))


def turn_90_left(speed, is_left):
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


def mark_cell(position, value):
    """Mark the cell in the map."""
    maze_map[position] = value


def get_cell(position):
    """Retrieve the value of a cell (default to unexplored if not visited)."""
    return maze_map.get(position, 0)


def initialize_plot():
    plt.ion()  # Enable interactive mode
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.set_title('Maze Visualization')
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    plt.grid(True)
    return fig, ax


def visualize_map(fig, ax):
    ax.clear()  # Clear the previous plot
    ax.set_aspect('equal')
    ax.set_title('Maze Visualization')
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)

    # Plot cells
    for (x, y), state in maze_map.items():
        if state == 1:  # Open path
            color = 'white'
        elif state == -1:  # Wall
            color = 'black'
        elif state == 0:  # Unexplored
            color = 'gray'

        # Draw the cell as a square
        rect = patches.Rectangle((x - 0.5, y - 0.5), 1, 1, linewidth=1, edgecolor='blue', facecolor=color)
        ax.add_patch(rect)

    # Plot current position
    ax.plot(current_position[0], current_position[1], 'ro')  # Red dot for current position

    plt.draw()
    plt.pause(0.05)  # Brief pause to allow visualization to update


# -------------------------
#   Main Loop
# -------------------------


def main():
    global lineFollower_color, ultrasonicSensor, distance, SPEED, \
        distance_left, distance_right, unjam_retries, current_position
    roll = board.get_roll()
    x = 0
    y = 0

    print(f"Distance: {distance}")
    print(f"Distance Left: {distance_left}")
    print(f"Distance Right: {distance_right}")
    print(f"Color: {lineFollower_color}")
    print(f"Roll: {roll}")

    # If on black line but the robot is tilted significantly => unjam
    if lineFollower_color == 'black' and float(roll) < -30.0:
        print("Detected tilt; attempting to unjam.")
        control.move_backward(int(50 * (unjam_retries + 1)), 500)
        unjam_retries += 1
    elif distance > 15:
        y += 1
        mark_cell((current_position[0], current_position[1] + 1), 1)
        control.push_forward(SPEED)
    else:
        control.stop()
        mark_cell((current_position[0], current_position[1] + 1), -1)  # Mark as wall
        sleep(0.5)

        # Measure distance to the left
        turn_90_left(speed=SPEED, is_left="left")

        # Reset to original position
        turn_90_left(speed=(SPEED * -1), is_left="none")

        # Measure distance to the right
        turn_90_left(speed=(SPEED * -1), is_left="right")

        sleep(0.5)
        # Compare left and right distances to decide the direction
        if distance_left > distance_right:
            print("Turning LEFT (More space to the left)")
            x -= 1
            control.sharp_left(SPEED, 1000)  # Adjust the turning time if necessary
        elif distance_right > distance_left:
            print("Turning RIGHT (More space to the right)")
            x += 1
            control.sharp_right(SPEED, 1000)  # Adjust the turning time if necessary
        else:
            print("Distances are equal or unclear, turning around.")
            turn_90_left(SPEED, is_left="none")
            sleep(0.05)
            turn_90_left(SPEED, is_left="none")
        sleep(0.5)

    current_position = (x, y)
    print(f"Current position: {x}, {y}")
    if current_position not in maze_map:
        maze_map[current_position] = 0  # Mark as unexplored


# Entrypoint
# Initialize plot

# Entrypoint
def entry_point():
    fig, ax = initialize_plot()
    board.set_tone(50, 500)
    ultrasonicSensor.read(get_distance)
    lineFollower.read(get_code)
    sleep(3)
    board.set_tone(100, 300)
    while True:
        ultrasonicSensor.read(get_distance)
        lineFollower.read(get_code)
        main()
        visualize_map(fig, ax)
        sleep(0.05)  # Minimum sleep time for maximum responsiveness
