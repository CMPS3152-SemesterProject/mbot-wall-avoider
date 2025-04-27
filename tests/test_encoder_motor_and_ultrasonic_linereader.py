import makeblock
from time import sleep
from makeblock.boards import MeAuriga
from EncoderController import EncoderController
from makeblock.modules.rj25 import Ultrasonic, LineFollower, EncoderMotor

# Add the COM port
makeblock.add_port("COM4")

# Connect to the MeAuriga board
board = MeAuriga.connect(BLE=True)

# Connect to the Ultrasonic sensor
ultrasonic = Ultrasonic(board, port=7)
linereader = LineFollower(board, port=6)


def on_received(value):
    print("distance:", value)


def on_line(value):
    print("line follower status:", value)

# Move forward
# encoder_controller = EncoderController(board, 1, 2)
# encoder_controller.move_forward(100, 500)
# sleep(3)
# encoder_controller.stop()
#
# # Move backward
# encoder_controller.move_backward(100, 500)
# sleep(3)
# encoder_controller.stop()
#
# # Turn Left
# encoder_controller.move_left(100, 500)
# sleep(3)
# # Sharp Left
# encoder_controller.sharp_left(100, 500)
# sleep(3)
#
# # Turn Right
# encoder_controller.move_right(100, 500)
# sleep(3)
# # Sharp Right
# encoder_controller.sharp_right(100, 500)
# sleep(3)
#
# encoder_controller.stop()

while True:
    ultrasonic.read(on_received)
    linereader.read(on_line)

    sleep(0.05)  # For Bluetooth, 0.02 is the minimum sleep time to avoid data loss in the communication
    # 0.05 is the recommended sleep time for Bluetooth communication
