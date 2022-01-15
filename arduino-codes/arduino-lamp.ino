#include<SPI.h>                 
#include <Wire.h>                        
#include<RF24.h>                 
const int RELAY_PIN = 3;
const int BUTTON_PIN = 2;

bool button_clicked = false;
char current_lamp_status = '0';

RF24 radio(9, 10) ;     
void setup(void) {
  pinMode(RELAY_PIN, OUTPUT);
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
      char newLampStatus = receivedMessage[2];
      Serial.println("set lamp to " + newLampStatus);   
      setLampRelay(newLampStatus);
    }
    
    Serial.println("-----");
  }
  //delay(10);
  if(digitalRead(BUTTON_PIN) == HIGH && !button_clicked)
  {
    button_clicked = true;
    toggleLamp();
    
  }
  else if(digitalRead(BUTTON_PIN) == LOW && button_clicked == true)
  {
    button_clicked = false;
  }
}

bool validMessage(String message){
    if((message[0] == 'B') && message[1] == 'X'){
      return true;
    }
    return false;
}

void setLampRelay(char newStatus)
{
  current_lamp_status = newStatus;
  if(newStatus == '1')
  {
    digitalWrite(RELAY_PIN, HIGH);
  }
  else if(newStatus == '0')
  {
    digitalWrite(RELAY_PIN, LOW);
  }
}

void toggleLamp()
{
  if(current_lamp_status == '0')
  {
    setLampRelay('1');
  }
  else if(current_lamp_status == '1')
  {
    setLampRelay('0');
  }
}
