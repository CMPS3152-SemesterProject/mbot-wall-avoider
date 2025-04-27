#include <MeAuriga.h>
#include <MeEncoderMotor.h>
#include <MeUltrasonicSensor.h>
#include <MeLineFollower.h>

MeEncoderMotor motorLeft(PORT1);
MeEncoderMotor motorRight(PORT2);
MeUltrasonicSensor ultrasonicSensor(PORT_7);
MeLineFollower lineFollower(PORT_6);

void setup() {
  motorLeft.begin();
  motorRight.begin();
  Serial.begin(9600);
}

void loop() {
  int distance = ultrasonicSensor.distanceCm();
  int lineStatus = lineFollower.readSensors();

  if (distance < 10) {
    // Avoid wall
    motorLeft.move(-50, 300);
    motorRight.move(-50, 300);
    delay(300);
    motorLeft.move(60, 700);
    motorRight.move(-60, 700);
    delay(700);
  } else if (lineStatus == S1_IN_S2_OUT || lineStatus == S1_OUT_S2_IN) {
    // Follow line
    motorLeft.runSpeed(40);
    motorRight.runSpeed(40);
  } else {
    // Move forward
    motorLeft.runSpeed(40);
    motorRight.runSpeed(-40);
  }

  delay(100);
}
