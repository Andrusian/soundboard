#include <SoftwareSerial.h>

#include <DFRobotDFPlayerMini.h>


//
//  It is assumed that this will be used with an external amp.
//
// PREFERABLY USE RED LEDs! Because of lower voltage drop.
// Yellow/green/blue won't work.
//
//----------------------------------------------------------------------
// PIN ASSIGNMENT DIAGRAM:
//
//                     GND o-----------o VCC
//                     PB7 o teensy2++ o PB6          
//                     PD0 o           o PB5             (interior)
//                     PD1 o           o PB4          
//                     PD2 o           o PB3   Mom    
//     Serial TX 1kR   PD3 o    oo     o PB2   Mom       o PE5
//     Serial RX       PD4 o           o PB1   Mom       o PE4
//                     PD5 o           o PB0   Mom    
//                     PD6 o           o PE7           
//                     PD7 o           o PE6
//                     PE0 o           o GND
//                     PE1 o           o AREF
//             Lat     PC0 o           o PF0   Lat   
//             Lat     PC1 o     o o   o PF1   Lat    Mom o PA4 o PA0  LEDON
//             Lat     PC2 o     o o   o PF2          Mom o PA5 o PA1  LEDRUN
//             Lat     PC3 o     o o   o PF3          Mom o PA6 o PA2
//             Mom     PC4 o  o  o o   o PF4   Mom    Mom o PA7 o PA3  DKmini STATUS
//             Mom     PC5 o           o PF5   Mom      
//             Mom     PC6 o           o PF6   Mom       o ALE
//             Mom     PC7 o---o-o-o---o PF7   Mom
//                             V G R
//                             C N S
//                             C D T
//
//
//  Mom - momentary button 
//  Lat - Latched button  
//  All buttons have pull up resistors enabled (so they are wired to ground).
//  ALL DKplayer GND PINS MUST BE GROUNDED!
//


#define LEDON    (PORTA |= (1<<0))
#define LEDOFF    (PORTA &= ~(1<<0))
#define LEDRUNON  (PORTA |= (1<<1))
#define LEDRUNOFF (PORTA &= ~(1<<1))

#define HIGH 1
#define LOW 0                   
#define LOOPDELAY 1000           // time delay of main loop ms
#define INTSCALER 10
#define BUSYPIN 31


SoftwareSerial mySoftwareSerial(4, 5); // RX, TX
#define DFPserial_RX 4  // DFP RX pin 2 connect to Arduino TX pin 5
#define DFPserial_TX 5  // DFP TX pin 3 connect to Arduino RX pin 4

DFRobotDFPlayerMini myDFPlayer;

void setup() {
  // put your setup code here, to run once:
// standard bootup...



  // initialize command queue

  // initialize IO pins...

  (DDRA |= (1<<0));      // PORT A has the 2 LEDs
  (DDRA |= (1<<1));

  DDRC =  0b00000000;     // port C is all inputs
  PORTC = 0b11111111;    // port C uses pull up resistors
  DDRB =  0b00000000;     // port B is all inputs
  PORTB = 0b11111111;    // port B uses pull up resistors
  DDRA&=~(1<<3);    // pin A3 is input for DFplayer status
  
  debugLights();

  delay(1000);

  mySoftwareSerial.begin(9600);
  Serial.begin(9600);
  
  Serial.println();
  Serial.println(F("DFRobot DFPlayer Mini Demo"));
  Serial.println(F("Initializing DFPlayer ... (May take 3~5 seconds)"));

;
  myDFPlayer.begin(mySoftwareSerial);
  delay(200);
  if (0) {  //Use softwareSerial to communicate with mp3.
    Serial.println(F("Unable to begin:"));
    Serial.println(F("1.Please recheck the connection!"));
    Serial.println(F("2.Please insert the SD card!"));
    while(true);
  }
  Serial.println(F("DFPlayer Mini online."));


  //----Set volume----
  myDFPlayer.volume(20);  //Set volume value (0~30).

  delay(3000);


  Serial.println(F("play 1"));
  myDFPlayer.play(1); delay(31000);
  myDFPlayer.play(2); delay(31000);
  myDFPlayer.play(3); delay(31000);
  myDFPlayer.play(4); delay(31000);
  myDFPlayer.play(5); delay(31000);
  myDFPlayer.play(6); delay(31000);
  myDFPlayer.play(7); delay(31000);
     


}



//---------------------------------------------------------------------------------------------

void loop() {
  int modifier=0;
  int value=0;
  unsigned int selected=0;

  delay(1000);
 
  // these buttons are latched and modify the
  // momentary button values. this vastly modifies the number
  // of sounds that can be played.

  unsigned char C=PINC;
  unsigned char B=PINB;

  unsigned char b128=!(C & (1<<3));
  unsigned char b64=!(C & (1<<2));
  unsigned char b32=!(C & (1<<1));
  unsigned char b16=!(C & (1<<0));
  
  if (b16) {
    modifier+=16;
  }
  if (b32) {
    modifier+=32;
  }
  if (b64) {
    modifier+=64;
  }
  if (b128) {
    modifier+=128;
  }
  
  unsigned char b12=!(B & (1<<0));
  unsigned char b13=!(B & (1<<1));
  unsigned char b14=!(B & (1<<2));
  unsigned char b15=!(B & (1<<3));
    
  // put your main code here, to run repeatedly:

  // we'll read the buttons one at a time
  // this means if two buttons are pressed, the
  // higher number button overrides the earlier one

  if (b12) {
    selected=12;
  }
  if (b13) {
    selected=13;
  }
  if (b14) {
    selected=14;
  }
  if (b15) {
    selected=15;
  }

  value=selected+modifier;

  // was a momentary button pressed?

  // phex(C);
  // phex(B);
  
  if (1) {

    // for debugging, blink some lights

    blinkLights(modifier,selected);
  }
  
}

//----------------------------------------------------------------------
void debugLights (void) {

#define DEBUGBLINKS 10
#define DEBUGTIME 50
  int j;

  for (j=1;j<=DEBUGBLINKS;j++) {
    LEDON;
    delay(DEBUGTIME);
    LEDOFF;
    
    LEDRUNON;
    delay(DEBUGTIME);
    LEDRUNOFF;
  }

  LEDON;
}

//----------------------------------------------------------------------
void blinkLights (int num1, int num2) {
  #define BLINKTIME 50
  int j;

  LEDOFF;
  delay(BLINKTIME);

  for (j=1;j<=num1;j++) {
    LEDON;
    delay(BLINKTIME);
    LEDOFF;
    delay(BLINKTIME);
  }

  for (j=1;j<=num2;j++) {
    LEDRUNON;
    delay(BLINKTIME);
    LEDRUNOFF;
    delay(BLINKTIME);
  }
}  
