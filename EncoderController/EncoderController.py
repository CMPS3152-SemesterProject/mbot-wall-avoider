from makeblock.modules.rj25 import EncoderMotor
from Util import Util as mix_in
from time import sleep

class EncoderController:
    def __init__(self, board, left_slot, right_slot):
        self.encoder_right = EncoderMotor(board, left_slot)
        self.encoder_left = EncoderMotor(board, right_slot)
        self.left_slot = left_slot
        self.right_slot = right_slot
        self.position = 0

        # For PID control
        self.Kp = 0.617
        self.Ki = 0.0
        self.Kd = 0.5
        self.previous_error = 0.0
        self.integral = 0.0

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
        # Invert the speed to make the robot turn right
        self.encoder_left.run(speed=(speed * -1))
        sleep(ms / 1000)
        self.stop()
        pass

    def sharp_right(self, speed, ms):
        self.encoder_left.run(speed)
        # Invert the speed to make the robot turn left
        self.encoder_right.run(speed)
        sleep(ms / 1000)
        self.stop()
        pass

    def turn_left(self, speed, ms):
        self.encoder_right.run(speed=(speed * -1))
        sleep(ms / 1000)
        self.stop()
        pass

    def turn_right(self, speed, ms):
        self.encoder_left.run(speed)
        sleep(ms / 1000)
        self.stop()
        pass

    def stop(self):
        self.encoder_left.run(0)
        self.encoder_right.run(0)
        pass

    # Custom functions ---------------------------------------------
    def push_forward(self, speed):
        self.encoder_left.run(speed)
        self.encoder_right.run(speed * -1)
        pass

    def push_backward(self, speed):
        self.push_forward(speed * -1)
        pass

    def turn_360(self, speed):
        if int(speed) < 0:
            timeout = (speed * -1)
        else:
            timeout = speed
        self.sharp_left(speed, int(1058 * (120 / timeout)))
        pass

    def set_speed(self, speed_left, speed_right):
        self.encoder_left.run(speed_left)
        self.encoder_right.run(speed_right)
        pass

    # PID Controller
    def lock(self, current_distance: float, desired_distance: float, base_speed: int):
        # Calculate the error and integral
        error = desired_distance - current_distance
        self.integral += error
        derivative = error - self.previous_error

        # Calculate the PID terms
        p_term = self.Kp * error
        i_term = self.Ki * self.integral
        d_term = self.Kd * derivative

        # Calculate the control signal
        control_signal = p_term + i_term + d_term

        # Update the previous error
        self.previous_error = error
        left_speed = base_speed + control_signal
        left_speed = mix_in.constrain(left_speed, 0, base_speed)

        right_speed = base_speed - control_signal
        right_speed = mix_in.constrain(right_speed, 0, base_speed)

        print(f"Right Dist: {current_distance} | Desired Dist: {desired_distance} |"
              f"L Speed: {left_speed} | R Speed: {right_speed} | Control Signal: {control_signal} | "
              f"Error: {error}\n")

        # Apply the control signal to the motors
        self.encoder_left.run(int(right_speed))
        self.encoder_right.run(int(left_speed) * -1)
        pass
