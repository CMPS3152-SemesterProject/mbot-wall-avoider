import makeblock
from EncoderController import EncoderController
from makeblock.boards import MeAuriga
from makeblock.modules.rj25 import LineFollower
from time import sleep

makeblock.add_port("COM4")
board = MeAuriga.connect()
lineFollower = LineFollower(board, port=6)
control = EncoderController(board, 1, 2)
lineFollower_color = 'black'
def set_color(value):
    global lineFollower_color
    if value is not 0:
        lineFollower_color = 'white'
    else:
        lineFollower_color = 'black'

    # print("color:", value)

def headToIsland():
    while True:
        if lineFollower_color is 'white':
            sleep(10)



def leaveIsland():
    counter = 0
    control.move_left(24,)


counter = 0
def main():
     sleep(1)
     lineFollower.read(set_color)

    while True:
        if lineFollower_color is 'white':
            sleep(1)
            control.move_backward(5, 200)
            control.move_left(20, 700)
            board.set_color(1,255,0,0)
            counter += 1
            if counter is 4:
                control.stop()
                control.sharp_right()

