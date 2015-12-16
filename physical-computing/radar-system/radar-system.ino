/* 
 * Lab 3
 * By: Daniel Speiser, Maria Shen, Mark Assad
 */
// library imports
#include <Servo.h>       // import servo library
// global variable declarations and initializations
Servo servo;             // create servo object to control a servo
int pwPin = 3;           // declare pw pin 3 for sonar depth tracker
int servoPin = 5;        // declare pin 5 as servo pin
int pos = 0;             // keep track of servo position
int startPos = 0;        // initial start position
int endPos = 0;          // end position
int increment = 0;       // angle degree in which to increment servo
bool isInput = false;    // flag for detecting if input has been given
float pulse, mm;         // calculate and store pulse and mm of sonar
// helper methods
/* 
 *  The parseInput method reads and parses serial input for
 *  servo rotation in the form of: int start, end, increment
 */
void parseInput() {
  isInput = true;                // set flag to true 
  startPos = Serial.parseInt();  // parse first int as start pos
  endPos = Serial.parseInt();    // parse second int as end pos
  increment = Serial.parseInt(); // parse third int as angle increment
}
/* 
 * The readSensor method pulses the pw pin to high
 * in order to allow the sonar depth tracker to 
 * read in and record an object's distance.
 */
void readSensor() {
  pulse = pulseIn(pwPin, HIGH); // set pw pin to high, record pulse
  mm = pulse;                   // mm is equal to pulse width
  delay(100);                   // delay 100ms for servo to reach position
}
/* 
 * The printReadings method prints the recorded depth
 * readings to the console. TODO: Implement with GUI
 */
void printReadings() {
  Serial.print(mm);
  Serial.print(",");
  Serial.println(pos);
}
/*
 * the rotate method rotates the servo in the in the given
 * angle range (0-180 degrees), angle increment, and direction
 */
void rotate(int startPos, int endPos, int increment, boolean dir) {
  if (dir)  // rotate if direction is forward 
    // rotate servo from start position to end position, moving by given increment
    for (pos = startPos; pos <= endPos; pos += increment)
      readSonarAndRotateServo(pos);
  else     // rotate backwards
    // rotate servo from end position to start position, moving by given increment
    for (pos = endPos; pos >= startPos; pos -= increment)
      readSonarAndRotateServo(pos);
}
/*
 * reads the sonar and rotates the servo together to accrue
 * distance readings along with the servo's rotation
 */
void readSonarAndRotateServo(int pos) {
    readSensor();               // call read sensor
    printReadings();            // display sensor readings
    servo.write(pos);            // move servo to position pos
    delay(100);                  // delay 100ms for servo to reach position
}
// initial setup
void setup() {
  Serial.begin(9600);      // opens serial port, sets data rate to 9600 bps
  pinMode(pwPin, INPUT);   // set pw pin for sonar depth tracker as input
  servo.attach(servoPin);  // attach servo to the servo pin declared above
}
// main loop
void loop() {
  if (Serial.available())     // if input is available
    parseInput();             // call parse helper
  else if (isInput == true) { // if there is input, start rotating servo
    // rotate servo from start position to end position, moving by given increment
    rotate(startPos, endPos, increment, true);  // call helper to rotate forward 
    rotate(startPos, endPos, increment, false); // call helper to rotate backward 
  }
}
