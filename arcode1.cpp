/* Dual Servo Sweep with Serial Control
 by BARRAGAN <http://barraganstudio.com>
 This example code is in the public domain.
 modified 8 Nov 2013
 by Scott Fitzgerald
 https://www.arduino.cc/en/Tutorial/LibraryExamples/Sweep
*/

#include <Servo.h>

Servo servo1; // create servo object for pin 8
Servo servo2; // create servo object for pin 10

int pos = 0; // variable to store the servo position
bool reverseCycle = false; // flag to track if we're in reverse cycle
bool running = false; // control if servos are moving (start stopped)
int speedDelay = 15; // delay between steps in milliseconds (fast by default)
unsigned long reverseStartTime = 0; // track when reverse cycle starts

void setup() {
  Serial.begin(9600);
  servo1.attach(8); // attaches the servo on pin 8
  servo2.attach(10); // attaches the servo on pin 10
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "START") {
      running = true;
      Serial.println("Started");
    }
    else if (command == "STOP") {
      running = false;
      Serial.println("Stopped");
    }
    else if (command.startsWith("SPEED:")) {
      speedDelay = command.substring(6).toInt();
      Serial.print("Speed set to: ");
      Serial.println(speedDelay);
    }
    else if (command.startsWith("SERVO1:")) {
      int angle = command.substring(7).toInt();
      servo1.write(angle);
      Serial.print("Servo1: ");
      Serial.println(angle);
    }
    else if (command.startsWith("SERVO2:")) {
      int angle = command.substring(7).toInt();
      servo2.write(angle);
      Serial.print("Servo2: ");
      Serial.println(angle);
    }
    else if (command.startsWith("REVERSE:")) {
      int val = command.substring(8).toInt();
      if (val == 1 && !reverseCycle) {
        reverseCycle = true;
        reverseStartTime = millis();
        Serial.println("Reverse mode ON");
      }
      else if (val == 0) {
        reverseCycle = false;
        Serial.println("Reverse mode OFF");
      }
    }
  }
  
  if (running) {
    // First 180 degree sweep (0 to 180)
    for (pos = 0; pos <= 180; pos += 1) {
      if (reverseCycle) {
        servo1.write(180 - pos); // servo1 reversed
      } else {
        servo1.write(pos); // servo1 forward
      }
      servo2.write(180 - pos); // servo2 counter direction
      delay(speedDelay);
    }
    
    // Second 180 degree sweep (0 to 180 again)
    for (pos = 0; pos <= 180; pos += 1) {
      if (reverseCycle) {
        servo1.write(180 - pos); // servo1 reversed
      } else {
        servo1.write(pos); // servo1 forward
      }
      servo2.write(180 - pos); // servo2 counter direction
      delay(speedDelay);
    }
    
    // Check if 120 seconds have passed in reverse mode
    if (reverseCycle && (millis() - reverseStartTime >= 120000)) {
      reverseCycle = false; // go back to normal
      Serial.println("Reverse mode timeout - back to normal");
    }
  } else {
    delay(100); // Small delay when stopped
  }
}