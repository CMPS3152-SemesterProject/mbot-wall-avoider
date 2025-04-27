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
lineFollower_color = 'black'  # Default color for line follower
counter = 0 #initialize variable, used to keep track of # of corners found
inside_Island = False #Initialize variable, used to trigger final destination found
looking_for_Island = False #Initialize variable, used to keep track if robot is within 4-walled cul-de-sac


#region Initialize line follower reading values

#Allows the conversion of line follower input from int to string 0 for Black, otherwise White
#Inputs : value, which is the line follower reading value
#Output : none
def set_color(value): #set color of line follower
    global lineFollower_color
    if int(value) != 0:
        lineFollower_color = 'white'
    else:
        lineFollower_color = 'black'
#endregion Initialize line follower reading values

#region turn control functions

#Allows robot to make a slight turn towards the left
#Input : left speed(lspeed) and right speed(rspeed) values
#Output : robot moving forward slightly to the left
def get_further_from_wall():
    control.controlled_turn(18, 35)

#Allows robot to make a slight turn towards the right
#Input : left speed and right speed values
#Output : robot moving forward slightly to the right
def get_closer_to_wall():
    control.controlled_turn(40, 18)

#Allows robot to stop then make a sharp turn to the left
#Input : left and right speed values
#Output : robot stops and makes a sharp turn to the left
def turn_180_degrees():
    control.stop()
    # make a 180-degree turn
    control.controlled_turn(0, 35)
    sleep(2.7)
    control.stop()

#Allows the robot to reverse then make a left turn, also increment counter
#Input : continuous reading of ultrasonic sensor being updated in distance variable
#Output : robot will stop, reverse slightly then make a left turn
def avoid_wall():
    global counter
    distance = ultrasonicSensor.get_distance(port=7)

    control.stop()  # stop when front wall is hit or too close
    control.move_backward(50, 300)  # Move back a bit
    # Turn left 90 degrees
    control.move_left(60, 700)
    control.stop()  # stop moving
    sleep(1)  # sleep for 1 second for line follower to update

    counter += 1
    # Update print statement
    print(f"\r\033[94mDistance:\033[0m \033[92m{distance}\033[0m | \033[94mLine color:\033[0m \033[92m{lineFollower_color}\033[0m", end="", flush=True)
#endregion

#Checks if robot has found Island to trigger a stop and if not lets it continue traversal (right hand rule)
#within four-walled cul-de-sac
#Input : line follower reading
#Output : Keeps robot traversing maze until island found which then triggers a stop, tone and lights
def head_to_island(): #head to island function
    global lineFollower_color
    global ultrasonicSensor
    global control
    global counter
    global inside_Island
    global looking_for_Island

    lineFollower.read(set_color)

    # Initial stop
    control.stop()
    #sets looking_for_island variable to true since four-walled cul-de-sac found at this point
    looking_for_Island = True
    print(f"Line follower color on entry: {lineFollower_color} \n")

    #Check line follower current reading and if it is not white continue traversal(right hand rule)
    if lineFollower_color != 'white':
        right_hand_rule()
        print("Line follower is not white", end="\n")
    #if line follower current reading is white (wall encountered)
    if lineFollower_color == 'white':
        avoid_wall()
        control.stop()
        #if counter=6 at this point 3 walls (island) have been found after entering four-walled cul-de-sac
        if counter == 6:
            inside_Island = True
        if inside_Island:
            print("\033[92m Inside Island\033[0m")
            #trigger stop then, tone and lights on robot
            control.stop()
            board.set_tone(50, 500)
            board.set_color(0,255,0,0)
            sleep(2)
            board.set_color(0,0,0,0)
            board.set_tone(50, 500)
            return #return to caller

#Allows robot to traverse maze, following the right hand rule
#Input : line follower reading and ultrasonic sensor for distance reading
#Output : Robot moves based on line follower reading (if wall encountered)
#and ultrasonic sensor for distance from right wall
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

        # Print with color, the distance and line color, and different colors to their values
        print(f"\r\033[94mDistance:\033[0m \033[92m{distance}\033[0m "
              f" | \033[94mLine color:\033[0m \033[92m{lineFollower_color}\033[0m "
              f"| \033[94mCounter :\033[0m \033[92m{counter}\033[0m "
              f" | \033[94mInside Island:\033[0m \033[92m{inside_Island}\033[0m ", end=" ", flush=True)

        if lineFollower_color == 'white': #if wall encountered
            print(" Wall encountered, Making left turn", end="\n", flush=False)
            avoid_wall()
            distance = ultrasonicSensor.get_distance(port=7)
            lineFollower.read(set_color)
            #if more than 3 walls have been found back to back
            if counter > 3:
                print(f"(Counter): {counter} Inside Loop, adjusting to enter island", end="\n")
                #if 4th wall has been encountered make a sharp left turn
                if counter == 4:
                    print("Making a 180-degree turn", end="", flush=True)
                    turn_180_degrees()
                    distance = ultrasonicSensor.get_distance(port=7)
                    lineFollower.read(set_color)

                #Call head to island function
                head_to_island()
                #exit right hand rule function if robot is within maze
                if inside_Island:
                     return
        #continuously check distance from right wall to robot
        if distance > 10:  # is far from the wall
            print("Moving closer to wall.", end=" ", flush=True)
            get_closer_to_wall()
            if distance > 25:
                #only reset counter to 0 if NOT within 4-walled cul-de-sac
                if not looking_for_Island:
                    print("(Not in Island): Resetting counter to 0", end="\n")
                    counter = 0

        if distance < 6:  # is too close to the wall
            print("Moving away from wall", end=" ", flush=True)
            get_further_from_wall()
        if 10 > distance > 6:  # is in the middle
            control.forward_non_stop(40)
            print("Moving forward at speed 40", end=" ", flush=True)

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
    print("\033[92m Starting main loop...\033[0m")

    #call right hand rule function
    right_hand_rule()

# Entry point
if __name__ == "__main__":
    main()

