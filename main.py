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

lineFollower_color = 'black'  # Default color
counter = 0

def set_color(value):
    global lineFollower_color
    if int(value) != 0:
        lineFollower_color = 'white'
    else:
        lineFollower_color = 'black'
    print("Updated color:", lineFollower_color)

def headToIsland():
    while True:
        if lineFollower_color == 'white':
            sleep(10)
            leave_island()
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

def leave_island():
    global counter
    counter = 0

def avoid_wall():
    global counter
    control.stop()
    control.move_backward(50, 200)
    control.move_left(50, 700)
    board.set_color(1, 255, 0, 0)
    counter += 1
    if counter == 4:
        control.stop()
        control.controlled_turn(4.5, 30)
        sleep(1.3)

def main():
    global lineFollower_color
    while True:
        # Continuously read the line follower data and update color
        lineFollower.read(set_color)
        print("Current Color:", lineFollower_color)

        if lineFollower_color == 'white':
            avoid_wall()
        else:
            control.forward_non_stop(20)

        sleep(0.2)  # Small delay to avoid excessive CPU usage

if __name__ == "__main__":
    main()
