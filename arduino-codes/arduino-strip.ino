#include<SPI.h>                 
#include <Wire.h>                        
#include<RF24.h>                 
#include<string.h>
#include <FastLED.h>

#define NUM_LEDS 114
#define DATA_PIN 3
CRGB leds[NUM_LEDS];
char currentAnimation = 'X';
char currentLightSwitch = '0';
uint8_t hue = 0;

RF24 radio(9, 10) ;     
void setup(void) {
  FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS); 

  
  while (!Serial) ;
  Serial.begin(9600) ;     
  Serial.println("Starting.. Setting Up.. Radio on..") ; 
  radio.begin();        
  radio.setPALevel(RF24_PA_MAX) ; 
  radio.setChannel(0x76) ;           
  const uint64_t pipe = 0xE0E0F0F1E0LL ;   
  radio.openReadingPipe(1, pipe) ;        
  radio.enableDynamicPayloads() ;
  radio.powerUp() ;          
  delay(500);
  redAll();
  delay(1000);
  blackAll();
  delay(500);

}


void loop(void) {

  radio.startListening() ;        // start listening forever
  char receivedMessage[32] = {0} ;   // set incmng message for 32 bytes
  if (radio.available()) {       // check if message is coming
    radio.read(receivedMessage, sizeof(receivedMessage));    
    //Serial.println(receivedMessage) ;    
    radio.stopListening() ;  
    String stringMessage(receivedMessage) ;   
    //delay(1000);
    if(validMessage(receivedMessage)){
        char lightSwitch = receivedMessage[3];
        currentLightSwitch = lightSwitch;
        if(lightSwitch == '0'){
          currentAnimation = 'X';
          blackAll();
          return;
        }
        if(receivedMessage[2] == 'A'){
            char animation = receivedMessage[4];
            currentAnimation = animation;
        }
        else if(receivedMessage[2] == 'C'){
              currentAnimation = 'X';
              String colorString = String(receivedMessage).substring(4, 12);
              //Serial.println("colorString: " + colorString);
              long color = strtol(colorString.c_str(), NULL, 16);
              for(int i=0; i<NUM_LEDS; i++){
                  leds[i] = color;
              }
       
              FastLED.show();
        }
        //Serial.print("switch: ");
        //Serial.println(lightSwitch);
    }
    
    //Serial.println("-----");
  }
  animate(currentAnimation, currentLightSwitch);
}


void animate(char animation, char lightSwitch){
  
  switch(animation){
    case '0':
      rgbWave();
      break;
    case '1':
      rgbAll();
      break;
    case '2':
      animation3();
      break;
    default:
      break;
  }
}

bool validMessage(String message){
    if((message[0] == 'B') && message[1] == 'X'){
      return true;
    }
    return false;
}

void redAll(){
  for(int i=0; i<NUM_LEDS; i++){
    leds[i] = CRGB::Red;
  }
  FastLED.show();
}

void blackAll(){
  for(int i=0; i<NUM_LEDS; i++){
    leds[i] = CRGB::Black;
  }
  FastLED.show();
}

void rgbWave(){
  for(int i = 0; i<NUM_LEDS; i++)
    {
      leds[i] = CHSV(hue + (i*(255/NUM_LEDS)), 255, 255);  
    }

    EVERY_N_MILLISECONDS(15)
    {
      hue++;  
    }

    FastLED.show();  
  
}
void rgbAll(){
  //Serial.println("animation 2");
  for(int i = 0; i<NUM_LEDS; i++)
    {
      leds[i] = CHSV(hue, 255, 255);  
    }

    EVERY_N_MILLISECONDS(15)
    {
      hue++;  
    }

    FastLED.show();  
}
void animation3(){
  //Serial.println("animation 3");
  blackAll();
}
