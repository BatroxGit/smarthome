#include<SPI.h>                 
#include <Wire.h>                        
#include<RF24.h>                 


RF24 radio(9, 10) ;     
void setup(void) {
  while (!Serial) ;
  Serial.begin(9600) ;     
  Serial.println("Starting.. Setting Up.. Radio on..") ; 
  radio.begin();        
  radio.setPALevel(RF24_PA_MAX) ; 
  radio.setChannel(0x76) ;           
  const uint64_t pipe = 0xE0E0F1F1E0LL ;   
  radio.openReadingPipe(1, pipe) ;        
  radio.enableDynamicPayloads() ;
  radio.powerUp() ;          
  delay(2000);
}

void loop(void) {

  radio.startListening() ;        // start listening forever
  char receivedMessage[32] = {0} ;   // set incmng message for 32 bytes
  if (radio.available()) {       // check if message is coming
    radio.read(receivedMessage, sizeof(receivedMessage));    
    Serial.println(receivedMessage) ;    
    radio.stopListening() ;  
    String stringMessage(receivedMessage) ;   
    //delay(1000);
    if(validMessage(receivedMessage)){
      Serial.println("set lamp to " + receivedMessage[2]);
    }
    
    Serial.println("-----");
  }
  //delay(10);
}

bool validMessage(String message){
    if((message[0] == 'B') && message[1] == 'X'){
      return true;
    }
    return false;
}
