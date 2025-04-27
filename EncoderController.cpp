#include "EncoderController.h"

EncoderController::EncoderController(uint8_t leftSlot, uint8_t rightSlot)
    : motorLeft(leftSlot), motorRight(rightSlot) {}

void EncoderController::moveForward(int speed, int duration) {
    motorLeft.move(speed, duration);
    motorRight.move(-speed, duration);
}

void EncoderController::moveBackward(int speed, int duration) {
    moveForward(-speed, duration);
}

void EncoderController::moveLeft(int speed, int duration) {
    motorRight.move(speed, duration);
    motorLeft.move(speed, duration);
}

void EncoderController::stop() {
    motorLeft.stop();
    motorRight.stop();
}

void EncoderController::controlledTurn(int leftSpeed, int rightSpeed) {
    motorLeft.runSpeed(leftSpeed);
    motorRight.runSpeed(-rightSpeed);
}

void EncoderController::forwardNonStop(int speed) {
    motorRight.runSpeed(-speed);
    motorLeft.runSpeed(speed);
}
