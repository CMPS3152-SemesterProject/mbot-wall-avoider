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

def set_color(value): #set color of line follower
    global lineFollower_color
    if int(value) != 0:
        lineFollower_color = 'white'
    else:
        lineFollower_color = 'black'

def head_to_island(): #head to island function

    global lineFollower_color
    global ultrasonicSensor
    global control
    global counter
    global inside_Island

    # Initial stop
    control.stop()
    sleep(1)
    print("\033[92m INSIDE ISLAND...\033[0m")  # Print in green

    while True and inside_Island:
        # Continuously read the line follower data and update color
        lineFollower.read(set_color)
        # Read ultrasonic distance
        distance = ultrasonicSensor.get_distance(port=7)
        # If the sensor reads 400, it's typically 'no object' or out of range.
        # Instead of forcing it to zero, we can keep it at 400 or set a default:

        print("\r" + " " * 50, end=" ")  # Clears the line
        # Add color to the distance and line color, and different colors to their values
        print(f"\r\033[94mDistance:\033[0m \033[92m{distance}\033[0m "
              f" | \033[94mLine color:\033[0m \033[92m{lineFollower_color}\033[0m "
              f"| \033[94mCounter :\033[0m \033[92m{counter}\033[0m "
              f" | \033[94mInside Island:\033[0m \033[92m{inside_Island}\033[0m ", end=" ", flush=True)

        if lineFollower_color == 'white':
            print("Stop 10 seconds.", end=" ", flush=True)
            sleep(10)
            leave_island_setup()
        if distance > 11: #is far from the wall
            print("Moving closer to wall.", end=" ", flush=True)
            get_closer_to_wall()
            if distance > 25:
                print("reseting counter to 0", end=" ", flush=True)
                counter = 0
        if distance < 7: #is too close to the wall
            print("Moving away form wall", end=" ", flush=True)
            get_further_from_wall()
        if 12 > distance > 7: #is in the middle
            control.forward_non_stop(35)
            print("Moving forward at speed 35.", end=" ", flush=True)

        # Small delay
        sleep(0.1)

def get_further_from_wall():
    control.controlled_turn(18, 35)

def get_closer_to_wall():
    control.controlled_turn(40, 18)

def leave_island_setup():

    global lineFollower_color
    global ultrasonicSensor
    global control
    global counter
    global inside_Island


    print("Leave Island Setup 180-degree turn v2", end=" ", flush=True)
    counter = 0
    control.move_backward(15, 1000)
    turn_180_degrees()
    avoid_wall()
    control.stop()
    control.move_backward(15, 700)


def turn_180_degrees():
    control.stop()
    # make a 180-degree turn
    control.controlled_turn(3, 28)
    sleep(3.3)

    # sleep(5.3)
    control.stop()

def turn_180_degrees_v2ii():
    control.stop()
    # make a 180-degree turn
    control.move_backward(25,1000)
    print("180 v2 turn", end=" ", flush=True)
    control.controlled_turn(-15,9)
    sleep(3.3)

    control.stop()

def avoid_wall():
    global counter
    control.stop() # stop when front wall is hit or too close
    board.set_color(5, 255, 0, 0) # set all LED to red
    control.move_backward(50, 300)  # Move back a bit
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
    global counter
    global inside_Island

    # Initial stop
    control.stop()
    sleep(1)
    print("\033[92m Starting main loop...\033[0m")  # Print in green

    while True:
        # Continuously read the line follower data and update color
        lineFollower.read(set_color)
        # Read ultrasonic distance
        distance = ultrasonicSensor.get_distance(port=7)
        # If the sensor reads 400, it's typically 'no object' or out of range.
        # Instead of forcing it to zero, we can keep it at 400 or set a default:

        print("\r" + " " * 50, end=" ")  # Clears the line
        # Add color to the distance and line color, and different colors to their values
        print(f"\r\033[94mDistance:\033[0m \033[92m{distance}\033[0m "
              f" | \033[94mLine color:\033[0m \033[92m{lineFollower_color}\033[0m "
              f"| \033[94mCounter :\033[0m \033[92m{counter}\033[0m "
              f" | \033[94mInside Island:\033[0m \033[92m{inside_Island}\033[0m ", end=" ", flush=True)

        if lineFollower_color == 'white':
            print(" Wall encountered, Making right turn", end="", flush=True)
            #check if we are in island for a 180-degree turn
            avoid_wall()
            if counter == 4:
                print("Inside Loop, adjusting to enter island", end="", flush=True)
                print("making a 180-degree turn.", end="", flush=True)
                turn_180_degrees()
                inside_Island = True
                # head to island
                head_to_island()
        if distance > 11: #is far from the wall
            print("Moving closer to wall.", end=" ", flush=True)
            get_closer_to_wall()
            if distance > 25:
                print("reseting counter to 0", end=" ", flush=True)
                counter = 0
        if distance < 7: #is too close to the wall
            print("Moving away form wall", end=" ", flush=True)
            get_further_from_wall()
        if 12 > distance > 7: #is in the middle
            control.forward_non_stop(35)
            print("Moving forward at speed 35.", end=" ", flush=True)

        # Small delay
        sleep(0.1)


# Entry point
if __name__ == "__main__":
    main()

