import makeblock

from EncoderController import EncoderController
from makeblock.boards import MeAuriga
from makeblock.modules.rj25 import LineFollower
from makeblock.modules.rj25 import Ultrasonic
from time import sleep

# -------------------------
#   Connect to Me Auriga
# -------------------------
makeblock.add_port("COM4")
board = MeAuriga.connect()

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
unjam_retries = 0
move_away_from_wall = False
lineFollower_color = 'black'  # Default color
counter = 0


def set_color(value):
    """
    Sets the global lineFollower_color based on
    the integer output of the line follower sensor.
    Typical raw values can be 0, 1, 2, 3, etc.
    You may need to adjust if your sensor outputs differently.
    """
    global lineFollower_color
    # Debug: print("Raw line follower value:", value)
    if int(value) == 3:
        lineFollower_color = 'white'
    elif int(value) == 2:
        lineFollower_color = 'right'
    elif int(value) == 1:
        lineFollower_color = 'left'
    else:
        lineFollower_color = 'black'
    print("Updated color:", lineFollower_color)


def get_further_from_right_wall():
    """
    Commands a left turn to move away from the right wall.
    Adjust these turn values as needed.
    """
    control.controlled_turn(13, -16)  # Slight left turn
    print("Turning left to get away from the right wall.")


def get_closer_to_right_wall():
    """
    Commands a right turn to move closer to the right wall.
    Adjust these values to fine-tune how it approaches the wall.
    """
    control.controlled_turn(22, -13)  # Slight right turn
    sleep(1.25)
    control.forward_non_stop(30)
    print("Turning right to get closer to the right wall.")


def avoid_wall(distance):
    """
    Handles a situation where the robot detects a wall
    directly in front or is otherwise in a corner.
    """
    control.stop()
    board.set_color(5, 255, 0, 0)  # Set all LEDs to red
    print("Avoiding wall. Distance:", distance)
    sleep(1)

    # Move backward slightly
    control.move_backward(50, 750)

    # Decide which way to turn based on lineFollower_color
    if (lineFollower_color == 'left') or (lineFollower_color == 'white' and distance <= 10):
        # Turn left
        control.move_left(28, 1450)
    elif lineFollower_color == 'right':
        # Turn right
        control.move_right(28, 1450)
    elif lineFollower_color == 'white':
        # If still white, just move backward a bit more
        control.move_backward(50, 700)

    # Move forward a bit to commit to the turn
    control.move_forward(28, 1650)
    control.stop()
    sleep(0.5)  # brief pause for sensors to update


def main():
    global lineFollower_color
    global ultrasonicSensor
    global unjam_retries
    global move_away_from_wall

    # Initial stop
    control.stop()
    sleep(1)
    print("Starting main loop...")

    while True:
        # Read ultrasonic distance
        distance = ultrasonicSensor.get_distance(port=7)
        # If the sensor reads 400, it's typically 'no object' or out of range.
        # Instead of forcing it to zero, we can keep it at 400 or set a default:
        if distance == 400:
            distance = 30  # Treat as some moderate distance
        print("Distance:", distance)

        # Read orientation
        yaw = board.get_yaw()
        roll = board.get_roll()
        pitch = board.get_pitch()
        print(f"Yaw: {yaw}, Roll: {roll}, Pitch: {pitch}")

        # Read line follower sensor and update color
        lineFollower.read(set_color)

        # Decide movement based on sensors
        # 1) If line follower says white/left/right => wall avoidance
        if lineFollower_color in ('white', 'left', 'right'):
            avoid_wall(distance)

        # 2) If on black line but the robot is tilted significantly => unjam
        elif lineFollower_color == 'black' and float(roll) < -30.0:
            print("Detected tilt; attempting to unjam.")
            control.move_backward(int(50 * (unjam_retries + 1)), 500)
            unjam_retries += 1

        # 3) If far from the wall or just finished moving away => get closer
        elif distance >= 5:
            get_closer_to_right_wall()
            sleep(0.5)
            move_away_from_wall = True

        # 4) If too close to the wall => get further away
        elif distance <= 2 or move_away_from_wall is True:
            get_further_from_right_wall()
            move_away_from_wall = False
            sleep(3)

        # 5) Otherwise, move forward
        else:
            print("Moving forward at speed 20.")
            control.forward_non_stop(20)

        # Reset unjam if we have done a couple attempts and robot is level
        if unjam_retries >= 2 and float(roll) > -5.0:
            print("Resetting unjam attempts.")
            unjam_retries = 0

        # Small delay
        sleep(0.1)


# Entry point
if __name__ == "__main__":
    main()
