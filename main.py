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
makeblock.add_port("COM3")
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
lineFollower_color = 'black'  # Default color
counter = 0


inside_Island = False
looking_for_Island = False

def set_color(value): #set color of line follower
    global lineFollower_color
    if int(value) != 0:
        lineFollower_color = 'white'
    else:
        lineFollower_color = 'black'

# def exit_island():
#

def head_to_island(): #head to island function

    global lineFollower_color
    global ultrasonicSensor
    global control
    global counter
    global inside_Island
    global looking_for_Island
    distance = ultrasonicSensor.get_distance(port=7)

    # Initial stop
    control.stop()
    looking_for_Island = True
    sleep(1)
    print("\033[92m INSIDE ISLAND...\033[0m")  # Print in green

    print(f"line follower color on entry: {lineFollower_color} \n")

    # Continuously read the line follower data and update color
    while lineFollower_color != 'white':
        right_hand_rule()
        print("Line follower is not white", end="\n")
    if lineFollower_color == 'white':
        control.stop()
        inside_Island = True
        if inside_Island:
            print("Is inside Island", end="\n")

            print("Stop 5 seconds.", end="\n")
            control.stop()
            board.set_tone(50, 500)
            return


def get_further_from_wall():
    control.controlled_turn(18, 35)

def get_closer_to_wall():
    control.controlled_turn(40, 18)

def turn_180_degrees():
    control.stop()
    # make a 180-degree turn
    control.controlled_turn(0, 28)
    sleep(2.7)

    # sleep(5.3)
    control.stop()

def right_turn():
    control.stop()  # stop when front wall is hit or too close
    control.move_backward(50, 300)  # Move back a bit
    # Turn left 90 degrees, might need some tweaking
    control.move_left(60, 700)
    control.stop()  # stop moving
    sleep(1)  # sleep for 1 second for line follower to update

def avoid_wall():
    global counter
    right_turn()
    counter += 1
    # Update print statement
    print(f"\r\033[94mDistance:\033[0m \033[92m{ultrasonicSensor.get_distance(port=7)}\033[0m | \033[94mLine color:\033[0m \033[92m{lineFollower_color}\033[0m", end="", flush=True)

def check_distance():
    global counter
    distance = ultrasonicSensor.get_distance(port=7)
    if distance > 10:  # is far from the wall
        print("Moving closer to wall.", end=" ", flush=True)
        get_closer_to_wall()
        if distance > 25:
            if not looking_for_Island:
                print("reset counter to 0", end="\n")
                counter = 0
            else:
                counter = 4
    if distance < 6:  # is too close to the wall
        print("Moving away form wall", end=" ", flush=True)
        get_further_from_wall()
    if 11 > distance > 7:  # is in the middle
        control.forward_non_stop(20)
        print("Moving forward at speed 35.", end=" ", flush=True)

def right_hand_rule():
    global inside_Island
    global lineFollower_color
    global ultrasonicSensor
    global control
    global counter
    global looking_for_Island

    while True:

        # Continuously read the line follower data and update color
        lineFollower.read(set_color)
        # Read ultrasonic distance
        distance = ultrasonicSensor.get_distance(port=7)
        # If the sensor reads 400, it's typically 'no object' or out of range.
        # Instead of forcing it to zero, we can keep it at 400 or set a default:


        # Add color to the distance and line color, and different colors to their values
        print(f"\r\033[94mDistance:\033[0m \033[92m{distance}\033[0m "
              f" | \033[94mLine color:\033[0m \033[92m{lineFollower_color}\033[0m "
              f"| \033[94mCounter :\033[0m \033[92m{counter}\033[0m "
              f" | \033[94mInside Island:\033[0m \033[92m{inside_Island}\033[0m ", end=" ", flush=True)

        if lineFollower_color == 'white':
            print(" Wall encountered, Making right turn", end="\n", flush=False)
            #check if we are in island for a 180-degree turn
            if not looking_for_Island:
                avoid_wall()
            else:
                right_turn()

            if counter == 4:
                print("Inside Loop, adjusting to enter island", end="\n")
                if not looking_for_Island:
                    print("making a 180-degree turn.", end="", flush=True)
                    turn_180_degrees()
                lineFollower.read(set_color)
                #inside_Island = True
                # exit_island()
                head_to_island()
                if inside_Island:
                    return
        check_distance()


        # Small delay
        sleep(0.1)


def main():
    global lineFollower_color
    global ultrasonicSensor
    global control
    global counter
    global looking_for_Island

    # Initial stop
    control.stop()
    sleep(1)
    print("\033[92m Starting main loop...\033[0m")  # Print in green

    if not inside_Island:
       right_hand_rule()
    #else:
        #board.set_color(0, 255,0,0)

# Entry point
if __name__ == "__main__":
    main()

