#ifndef ENCODERCONTROLLER_H
#define ENCODERCONTROLLER_H

#include <MeAuriga.h>
#include <MeEncoderMotor.h>

class EncoderController {
public:
    EncoderController(uint8_t leftSlot, uint8_t rightSlot);
    void moveForward(int speed, int duration);
    void moveBackward(int speed, int duration);
    void moveLeft(int speed, int duration);
    void stop();
    void controlledTurn(int leftSpeed, int rightSpeed);
    void forwardNonStop(int speed);

private:
    MeEncoderMotor motorLeft;
    MeEncoderMotor motorRight;
};

#endif
