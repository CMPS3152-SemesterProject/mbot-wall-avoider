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
get_away_please = False

lineFollower_color = 'black'  # Default color
counter = 0


def set_color(value):  # Set color of line follower
    global lineFollower_color
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
    # Swerve to the left
    control.controlled_turn(13, int(16 * -1))


def get_closer_to_right_wall():
    # Swerve to the right
    control.controlled_turn(22, int(13 * -1))
    sleep(1.25)
    control.forward_non_stop(30)


def avoid_wall(distance):
    global counter
    control.stop()  # Stop when front wall is hit or too close
    board.set_color(5, 255, 0, 0)  # Set all LED to red
    sleep(1)
    # We will only do a left turn if we are on the white line
    if (lineFollower_color == 'left') or (lineFollower_color == 'white' and distance <= 10):
        control.move_backward(50, 750)  # Move back a bit
        # A white line is classified as a wall to our right and a wall to our front
        control.move_left(28, 1450)
    elif lineFollower_color == 'right':  # If we are on black line, we will do a right turn
        control.move_backward(50, 750)  # Move back a bit
        # A black line is classified as a wall to our front and no wall to our right
        control.move_right(28, 1450)
    elif lineFollower_color == 'white':
        control.move_backward(50, 700)
    # Commit to the turn
    control.move_forward(28, 1650)
    # else:
    #     control.forward_non_stop(15)
    control.stop()  # Stop moving
    sleep(0.5)  # Sleep for 0.5 second for line follower to update
    # counter += 1


def main():
    global lineFollower_color
    global ultrasonicSensor
    global unjam_retries
    global get_away_please

    control.stop()
    sleep(1)
    while True:
        distance = ultrasonicSensor.get_distance(port=7)
        if distance == 400 and lineFollower_color == 'black':
            distance = 0  # Set distance to 0 if it's 400 (as it's the default value no matter what)
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
        control.stop()
        if lineFollower_color == 'white' or lineFollower_color == 'left' or lineFollower_color == 'right':
            avoid_wall(distance)
            # Check if we are in island for a 180-degree turn
            # if counter == 4:
            #     turn_180_degrees()
                # Head to island
                # head_to_island()
        # elif lineFollower_color == 'black' and distance >= 5:  # If we are on black line, we will do a right turn
        #     # A black line is classified as a wall to our right and no wall to our front
        #     control.move_right(50, 700)
        # Yank the robot out of the wall if it crashes
        elif lineFollower_color == 'black' and float(roll) < -30.0:
            control.move_backward(int(50 * unjam_retries), 500)
            unjam_retries += 1
        elif distance >= 5 or get_away_please is True:  # Is far from the wall
            get_closer_to_right_wall()
            sleep(0.5)
            get_away_please = False
        elif distance <= 2:  # Is too close to the wall
            get_further_from_right_wall()
            get_away_please = True
            sleep(3)
        else:
            control.forward_non_stop(20)
        # We're on level ground, reset the unjam retries
        if unjam_retries >= 2 and float(roll) > 0:
            # "Do not worry son, I am here"
            unjam_retries = 0
        # #NEED SOME TWEAKING BASED ON PERFORMANCE WITH SENSORS
        sleep(0.1)  # Small delay to avoid excessive CPU usage


# Call the main startup function
if __name__ == "__main__":
    main()
