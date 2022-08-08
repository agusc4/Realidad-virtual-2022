
#include <SPI.h>
#include <RF24.h>
#include <nRF24L01.h>

#define CE_PIN 7
#define CSN_PIN 8
String cad,cad1,cad2;
int pos;
byte direccion[5] ={'c','a','n','a','l'};
RF24 radio(CE_PIN, CSN_PIN); // Create a Radio
int velocidad[3]; 

void setup() {

  Serial.begin(115200); 
  radio.begin();
  radio.setDataRate(RF24_250KBPS);
  //radio.setRetries(3,5); // delay, count
  radio.openWritingPipe(direccion);
  velocidad[0]=150; //izquierda
  velocidad[1]=150; //derecha
}

void loop() {
  
  if (Serial.available() > 0) {
    cad = Serial.readString(); 
    pos = cad.indexOf(',');
    cad1= cad.substring(0,pos);
    cad2= cad.substring(pos+1);
    if(velocidad[0] != cad1.toInt()){
      velocidad[0] = cad1.toInt();             
    }
    if(velocidad[1] != cad2.toInt()){
      velocidad[1] = cad2.toInt();  
      }  
      }
  bool ok = radio.write(velocidad, sizeof(velocidad));

}
 
