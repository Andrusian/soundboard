//#include <DFRobot_DF1201S.h>           // FOR DFPlayer PRO VERSION
// is using the mini, much of the DFPlayer commands has to change
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
//             Mom     PC4 o  o  o o   o PF4   Mom    Mom o PA7 o PA3  
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
//


#define LEDON    (PORTA |= (1<<0))
#define LEDOFF    (PORTA &= ~(1<<0))
#define LEDRUNON  (PORTA |= (1<<1))
#define LEDRUNOFF (PORTA &= ~(1<<1))

                
#define LOOPDELAY 1000           // time delay of main loop ms
#define INTSCALER 10
#define BUSYPIN 31


// SoftwareSerial mySoftwareSerial(4, 5); // RX, TX
// #define DFPserial_RX 4  // DFP RX pin 2 connect to Arduino TX pin 5
// #define DFPserial_TX 5  // DFP TX pin 3 connect to Arduino RX pin 4

void setup() {

  // initialize command queue

  // initialize IO pins...

  DDRA = 0b00000011;       // bottom 2 pins are outputs
  PORTA = 0b11111100;      // rest have pull-up resistors

  DDRC =  0b00000000;     // port C is all inputs
  PORTC = 0b11111111;     // port C uses pull up resistors
  DDRB =  0b00000000;     // port B is all inputs
  PORTB = 0b11111111;     // port B uses pull up resistors
  DDRF =  0b00000000;     // port F is all inputs
  PORTF = 0b11111111;     // port B uses pull up resistors
  
  debugLights();

  delay(1000);

   // Keyboard.println(F("soundboard hello!"));


  
  //  DF1201Serial.begin(115200);
  // while(!DF1201S.begin(DF1201SSerial)){
    //Serial.println("Init failed, please check the wire connection!");
    //delay(1000);
  //}

}

//--------------------------------------------------------------------------------------------

unsigned int getDFStatus() {

  return !(PORTA & (1<<3));
}

//---------------------------------------------------------------------------------------------

void loop() {
  int modifier=0;
  unsigned int selected=256;

  delay(1000);
 
  // these buttons are latched and modify the
  // momentary button values. this vastly modifies the number
  // of sounds that can be played.

  unsigned char A=PINA;
  unsigned char C=PINC;
  unsigned char B=PINB;
  unsigned char F=PINF;

  // find position of latched buttons first...

  unsigned char b128=!(C & (1<<3));
  unsigned char b64=!(C & (1<<2));
  unsigned char b32=!(C & (1<<1));
  unsigned char b16=!(C & (1<<0));

  unsigned char bclr=!(F & (1<<1));
  unsigned char brun=!(F & (1<<0));
  
  if (b16) {
    modifier+=16; // red latched button
  }
  if (b32) {     // blue right latched button
    modifier+=32;
  }
  if (b64) {    // blue left latched button
    modifier+=64;
  }
  if (b128) {   // white latched button
    modifier+=128;
  }

  // buttons are numbered top left
  // to bottom right - these are momentaries

  unsigned char b0=!(B & (1<<3));   // top yellow bank
  unsigned char b1=!(B & (1<<2));
  unsigned char b2=!(B & (1<<1));
  unsigned char b3=!(B & (1<<0));
  
  unsigned char b4=!(F & (1<<6));   // blue bank
  unsigned char b5=!(F & (1<<7));
  unsigned char b6=!(F & (1<<4));
  unsigned char b7=!(F & (1<<5));
  
  unsigned char b8=!(C & (1<<6));   // black bank
  unsigned char b9=!(C & (1<<7));
  unsigned char b10=!(C & (1<<4));
  unsigned char b11=!(C & (1<<5));
   
  unsigned char b12=!(F & (1<<7));   // yellow bank
  unsigned char b13=!(F & (1<<6));
  unsigned char b14=!(F & (1<<4));  
  unsigned char b15=!(F & (1<<5));

  Serial.print (A,BIN);
  Serial.print (" ");
  Serial.print (B,BIN);
  Serial.print (" ");
  Serial.print (C,BIN);
  Serial.print (" ");
  Serial.print (F,BIN);
  Serial.println (" ");
  Serial.println("");
  
  // lower number pressed button
  // overrides higher one

  if (b0) {
    selected=0;
  }
  else if (b1) {
    selected=1;
  }
  else if (b2) {
    selected=2;
  }
  else if (b3) {
    selected=3;
  }
  else if (b4) {
    selected=4;
  }
  else if (b5) {
    selected=5;
  }
  else if (b6) {
    selected=6;
  }
  else if (b7) {
    selected=7;
  }
  else if (b8) {
    selected=8;
  }
  else if (b9) {
    selected=9;
  }
  else if (b10) {
    selected=10;
  }
  else if (b11) {
    selected=11;
  }  
  else if (b12) {
    selected=12;
  }
  else if (b13) {
    selected=13;
  }
  else if (b14) {
    selected=14;
  }
  else if (b15) {
    selected=15;
  }

  unsigned int value=selected+modifier;

  // was a momentary button pressed?

  
//  if (selected!=256) {
//    Serial.println(F("selected:"));
//    Serial.print(selected,DEC);
//    Serial.print(" ");
//    Serial.print(value,DEC);
//    Serial.println("");
//  }
  
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
