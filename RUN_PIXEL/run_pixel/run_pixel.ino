// NeoPixel Ring simple sketch (c) 2013 Shae Erisson
// released under the GPLv3 license to match the rest of the AdaFruit NeoPixel library
#include <Adafruit_NeoPixel.h>

// Which pin on the Arduino is connected to the NeoPixels?
#define PIN            1

// How many NeoPixels are attached to the Arduino?
#define NUMPIXELS      16

// When we setup the NeoPixel library, we tell it how many pixels, and which pin to use to send signals.
// Note that for older NeoPixel strips you might need to change the third parameter--see the strandtest
// example for more information on possible values.
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

int delayval = 500; // delay for half a second



//// ANIM.

void setPixel(uint8_t r, uint8_t g, uint8_t b,int nPix)
{
  
    // pixels.Color takes RGB values, from 0,0,0 up to 255,255,255
    pixels.setPixelColor(nPix%NUMPIXELS, pixels.Color(r,g,b)); // Moderately bright green color.
  
}

void setBlocks(uint8_t r, uint8_t g, uint8_t b,int first=0,int last=NUMPIXELS)
{
  for(int i=first;i<last;i++){
    // pixels.Color takes RGB values, from 0,0,0 up to 255,255,255
    pixels.setPixelColor(i%NUMPIXELS, pixels.Color(r,g,b)); // Moderately bright green color.
  }
}

void flightFlash()
{

  int block=random(0,15);
  for(int i=0;i<5;i++){
  setPixel(50,50,50,block+i);pixels.show();
  delay(3*i*i+10);
  }


  setBlocks(0,0,0);pixels.show();delay(10*random(5,11));
  

  for(int i=0;i<5;i++){
  setPixel(50,0,0,block+i+7);pixels.show();
  delay(3*i*i+10);
  }

  setBlocks(0,0,0);pixels.show();
  delay(30);

 /* int rvar=random(0,100);
  //if(rvar<50)
  {
  setBlocks(50,0,0,block+5,block+9);
  //pixels.show();
  //delay(rvar/2);
  //setBlocks(0,0,0);
  setBlocks(50,50,50,block+12,block+16);
  pixels.show();
  delay(rvar/10);
  
  delay(rvar);
  }*/
  

  setBlocks(0,0,0);pixels.show();
}


void reverseRoll()
{
  
  int a=random(0,16);
  int b=8 + a;

  for(int i=0;i<64;i++){
  setBlocks(0,0,0);
  setPixel(0,0,50,a+i);
  setPixel(50,0,0,b+i);
  
  pixels.show();
  
  delay((64-i+5)*(64-i+5)/70);
  }

  delay(50);
  
  
  //Reverse Roll
  //for(int i=63;i>=0;i--){

  // Funky Roll
  for(int i=0;i<=63;i++){
  setBlocks(0,0,0);
  setPixel(50,0,0,a+i);
  setPixel(0,0,50,b+i);
  pixels.show();
  
  delay((i+5)*(i+5)/70);
  }
}


void chase()
{
  int del=random(10,70);
  
  /////////////// CHASE COLORS
  for(int i=0;i<8;i++)
  {
    setBlocks(0,0,0);
    setPixel(0,0,50,i);
    pixels.show();
    delay(del);
  }
  
  for(int i=8;i<16;i++)
  {
    setBlocks(0,0,0);
    setPixel(50,0,0,i);
    pixels.show();
    delay(del);
  }
  /////////////// CHASE COLORS
  
}

void sweetRoll()
{
  setBlocks(0,0,0);
  pixels.show();
  
  for(int i=0;i<8;i++)
  {
    setPixel(0,0,50,i);
    setPixel(50,0,0,i+8);
    pixels.show();
    delay((i+5)*(i+5)/2);
  }

  for(int i=0;i<24;i++)
  {
    setBlocks(0,0,50,i,i+8);
    setBlocks(50,0,0,i+8,i+16);
    pixels.show();
    delay((24-i)*(24-i)/10);
  }

  for(int i=0;i<8;i++)
  {
    setPixel(0,0,0,i);
    setPixel(0,0,0,i+8);
    pixels.show();
    delay((i+5)*(i+5)/2);
  }
}

//// ANIM.

void setup() {
  pixels.begin(); // This initializes the NeoPixel library.
}

void loop() {
  // For a set of NeoPixels the first NeoPixel is 0, second is 1, all the way up to the count of pixels minus one.


  //while(1) { flightFlash();; delay(1000);}
  
  char rvar=random(0,100);

  int global_delay = 1000;

  
  if(rvar<70)flightFlash();
  else if (rvar<85)chase();
  else if (rvar<95)sweetRoll();
  else reverseRoll();
  //
  setBlocks(0,0,0);pixels.show();
  delay(global_delay + rvar * 70);

}
