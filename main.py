import makeblock
# import os
import sys

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
counter = 0

def set_color(value): #set color of line follower
    global lineFollower_color
    if int(value) != 0:
        lineFollower_color = 'white'
    else:
        lineFollower_color = 'black'

def head_to_island(): #head to island function
    while True:
        if lineFollower_color == 'white': #break inside island for 10 seconds
            control.stop()
            sleep(10)
            leave_island_setup() # gets a bit away frm wall
            turn_180_degrees() #180-degree turn
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
                control.forward_non_stop(25)
            # Update print statement
            print(f"\r\033[94mDistance:\033[0m \033[92m{distance}\033[0m | \033[94mLine color:\033[0m \033[92m{lineFollower_color}\033[0m", end="", flush=True)

def get_further_from_wall():
    control.controlled_turn(13, 26)

def get_closer_to_wall():
    control.controlled_turn(25, 13)

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
    # Update print statement
    print(f"\r\033[94mDistance:\033[0m \033[92m{ultrasonicSensor.get_distance(port=7)}\033[0m | \033[94mLine color:\033[0m \033[92m{lineFollower_color}\033[0m", end="", flush=True)


def main():
    global lineFollower_color
    global ultrasonicSensor
    global control

    # Initial stop
    control.stop()
    sleep(1)
    print("\033[92mStarting main loop...\033[0m")  # Print in green

    while True:
        # Continuously read the line follower data and update color
        lineFollower.read(set_color)
        # Read ultrasonic distance
        distance = ultrasonicSensor.get_distance(port=7)
        # If the sensor reads 400, it's typically 'no object' or out of range.
        # Instead of forcing it to zero, we can keep it at 400 or set a default:
        if distance == 400:
            distance = 0  # Treat as some moderate distance (turn right)

        print("\r" + " " * 50, end="")  # Clears the line
        # Add color to the distance and line color, and different colors to their values
        print(f"\r\033[94mDistance:\033[0m \033[92m{distance}\033[0m | \033[94mLine color:\033[0m \033[92m{lineFollower_color}\033[0m", end="", flush=True)

        if lineFollower_color == 'white':
            avoid_wall()
            #check if we are in island for a 180-degree turn
            if counter == 4:
                turn_180_degrees()
                # head to island
                head_to_island()
        elif distance > 12: #is far from the wall
            get_closer_to_wall()
        elif distance < 7: #is too close to the wall
            get_further_from_wall()
        else:
            control.forward_non_stop(30)
            print("Moving forward at speed 30.", end="", flush=True)

        # Small delay
        sleep(0.2)


# Entry point
if __name__ == "__main__":
    main()

