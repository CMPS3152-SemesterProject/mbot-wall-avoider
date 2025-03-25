import makeblock
from time import sleep
from makeblock.boards import MeAuriga
from EncoderController import EncoderController
from makeblock.modules.rj25 import Ultrasonic, LineFollower, EncoderMotor

# Add the COM port
makeblock.add_port("COM4")

# Connect to the MeAuriga board
board = MeAuriga.connect()

# Connect to the Ultrasonic sensor
ultrasonic = Ultrasonic(board, port=6)
linereader = LineFollower(board, port=10)


def on_received(value):
    print("distance:", value)


def on_line(value):
    print("line follower status:", value)

# Move forward
encoder_controller = EncoderController(board, 1, 2)
encoder_controller.move_forward(100, 500)
sleep(3)
encoder_controller.stop()

# Move backward
encoder_controller.move_backward(100, 500)
sleep(3)
encoder_controller.stop()

# Turn Left
encoder_controller.move_left(100, 500)
sleep(3)
# Sharp Left
encoder_controller.sharp_left(100, 500)
sleep(3)

# Turn Right
encoder_controller.move_right(100, 500)
sleep(3)
# Sharp Right
encoder_controller.sharp_right(100, 500)
sleep(3)

encoder_controller.stop()

while True:
    ultrasonic.read(on_received)
    linereader.read(on_line)

    sleep(1)
