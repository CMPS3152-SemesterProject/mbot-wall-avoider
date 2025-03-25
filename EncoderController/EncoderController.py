from makeblock.modules.rj25 import EncoderMotor
from time import sleep


class EncoderController:
    def __init__(self, board, left_slot, right_slot):
        self.encoder_right = EncoderMotor(board, left_slot)
        self.encoder_left = EncoderMotor(board, right_slot)
        self.left_slot = left_slot
        self.right_slot = right_slot
        self.position = 0

    def move_forward(self, speed, ms):
        self.encoder_left.run(speed)
        self.encoder_right.run(speed * -1)
        sleep(ms / 1000)
        self.stop()
        pass

    def move_backward(self, speed, ms):
        self.move_forward(speed * -1, ms)
        pass

    def sharp_left(self, speed, ms):
        self.encoder_right.run(speed=(speed * -1))
        sleep(ms / 1000)
        self.stop()
        pass

    def sharp_right(self, speed, ms):
        self.encoder_left.run(speed)
        sleep(ms / 1000)
        self.stop()
        pass

    def stop(self):
        self.encoder_left.run(0)
        self.encoder_right.run(0)
        pass