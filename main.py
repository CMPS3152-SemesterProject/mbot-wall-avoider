import makeblock

from EncoderController import EncoderController
from makeblock.boards import MeAuriga
from makeblock.modules.rj25 import LineFollower
from makeblock.modules.rj25 import Ultrasonic
from time import sleep

makeblock.add_port("COM4")
board = MeAuriga.connect()
lineFollower = LineFollower(board, port=6)
ultrasonicSensor = Ultrasonic(board, port=7)
control = EncoderController(board, 1, 2)
unjam_retries = 0

lineFollower_color = 'black'  # Default color
counter = 0


def set_color(value):  # Set color of line follower
    global lineFollower_color
    if int(value) != 0:
        lineFollower_color = 'white'
    else:
        lineFollower_color = 'black'
    print("Updated color:", lineFollower_color)


def head_to_island():  # Head to island function
    while True:
        if lineFollower_color == 'white':
            control.stop()
            sleep(10)
            leave_island_setup()
            turn_180_degrees()
            control.stop()
            sleep(.5)
            continue
        else:
            distance = ultrasonicSensor.get_distance(port=7)
            if distance > 12:
                control.controlled_turn(30, 11.5)
            elif distance < 5:
                get_further_from_wall()
            elif distance > 7:
                get_closer_to_wall()
            else:
                control.forward_non_stop(15)


def get_further_from_wall():
    control.controlled_turn(13, 26)


def get_closer_to_wall():
    control.controlled_turn(20, 13)


def leave_island_setup():
    global counter
    counter = 0
    control.stop()
    control.move_backward(15, 300)


def turn_180_degrees():
    control.stop()
    sleep(.3)
    # make a 180-degree turn
    control.controlled_turn(5, 28)
    sleep(1.3)
    # stop
    control.stop()


def avoid_wall():
    global counter
    control.stop()  # Stop when front wall is hit or too close
    board.set_color(5, 255, 0, 0)  # Set all LED to red
    control.move_backward(50, 400)  # Move back a bit
    # Turn left 90 degrees, might need some tweaking
    control.move_left(50, 700)
    control.stop()  # Stop moving
    sleep(1)  # Sleep for 1 second for line follower to update
    counter += 1


def main():
    global lineFollower_color
    global ultrasonicSensor
    global unjam_retries

    control.stop()
    sleep(1)
    while True:
        distance = ultrasonicSensor.get_distance(port=7)
        print("Distance:", distance)
        yaw = board.get_yaw()
        roll = board.get_roll()
        pitch = board.get_pitch()
        print("Yaw:", yaw)
        print("Roll:", roll)
        print("Pitch:", pitch)
        print(float(roll) < -30.0, float(pitch) < -1.0)
        # Continuously read the line follower data and update color
        lineFollower.read(set_color)
        if lineFollower_color == 'white':
            avoid_wall()
            # Check if we are in island for a 180-degree turn
            if counter == 4:
                turn_180_degrees()
                # Head to island
                head_to_island()
        # Yank the robot out of the wall if it crashes
        elif distance >= 12 and lineFollower_color == 'black' and float(roll) < -30.0:
            control.move_backward(int(50 * unjam_retries), 500)
            unjam_retries += 1
        elif distance > 12:  # Is far from the wall
            get_closer_to_wall()
        elif distance < 5:  # Is too close to the wall
            get_further_from_wall()
        else:
            control.forward_non_stop(15)
        # We're on level ground, reset the unjam retries
        if unjam_retries >= 2 and float(roll) > 0:
            # "Do not worry son, I am here"
            unjam_retries = 0
        # #NEED SOME TWEAKING BASED ON PERFORMANCE WITH SENSORS
        sleep(0.1)  # Small delay to avoid excessive CPU usage


# Call the main startup function
if __name__ == "__main__":
    main()
