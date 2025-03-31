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
board = MeAuriga.connect(BLE=False)

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

def set_color(value): #set color of line follower
    global lineFollower_color
    if int(value) != 0:
        lineFollower_color = 'white'
    elif int(value) == 2:
        lineFollower_color = 'right'
    elif int(value) == 1:
        lineFollower_color = 'left'
    else:
        lineFollower_color = 'black'
    print("Updated color:", lineFollower_color)

def head_to_island(): #head to island function
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
    control.stop() # stop when front wall is hit or too close
    board.set_color(5, 255, 0, 0) # set all LED to red
    control.move_backward(50, 400)  # Move back a bit
    # Turn left 90 degrees, might need some tweaking
    control.move_left(50, 700)
    control.stop() #stop moving
    sleep(1) #sleep for 1 second for line follower to update

    counter += 1


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
        # Continuously read the line follower data and update color
        lineFollower.read(set_color)
        # Read ultrasonic distance
        distance = ultrasonicSensor.get_distance(port=7)
        # If the sensor reads 400, it's typically 'no object' or out of range.
        # Instead of forcing it to zero, we can keep it at 400 or set a default:
        if distance == 400:
            distance = 0  # Treat as some moderate distance (turn right)
        print("Distance:", distance)

        # Read orientation
        yaw = board.get_yaw()
        roll = board.get_roll()
        pitch = board.get_pitch()
        print(f"Yaw: {yaw}, Roll: {roll}, Pitch: {pitch}")

        # ultrasonicSensor.read(set_distance)
        print(distance)
        if lineFollower_color in ('white', 'left', 'right'):
            avoid_wall()
            #check if we are in island for a 180-degree turn
            if counter == 4:
                turn_180_degrees()
                # head to island
                head_to_island()
        # 2) If on black line but the robot is tilted significantly => unjam
        elif lineFollower_color == 'black' and float(roll) < -30.0:
            print("Detected tilt; attempting to unjam.")
            control.move_backward(int(50 * (unjam_retries + 1)), 500)
            unjam_retries += 1
        elif distance > 12: #is far from the wall
            get_closer_to_wall()
        elif distance < 7: #is too close to the wall
            get_further_from_wall()
        else:
            control.forward_non_stop(20)
            print("Moving forward at speed 20.")
            control.forward_non_stop(20)

        # Reset unjam if we have done a couple attempts and robot is level
        if unjam_retries >= 2 and float(roll) > -5.0:
            print("Resetting unjam attempts.")
            unjam_retries = 0

        # Small delay
        sleep(0.05)


# Entry point
if __name__ == "__main__":
    main()
