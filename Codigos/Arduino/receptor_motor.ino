
#include <SPI.h>
#include <RF24.h>
#include <nRF24L01.h>
#define CE_PIN 7
#define CSN_PIN 8

RF24 radio(CE_PIN, CSN_PIN);

byte direccion[5] ={'c','a','n','a','l'}; 

int velocidad[4];

//RUEDA DERECHA
int ENB_IZQ = 6;
int IN3 = 9;
int IN4 = 10;

//RUEDA IZQUIERDA
int ENA_DER = 3;
int IN1 = 5;
int IN2 = 4;

int v_der = 0;
int v_izq = 0;


int speed = 0;  

int pinMotorA[3] = { ENA_DER, IN1, IN2 };
int pinMotorB[3] = { ENB_IZQ, IN3, IN4 };

void setup()
{

  Serial.begin(115200); // Iniciamos la comunicacion serie hacia el Monitor Serie en la PC
  radio.begin();
  radio.openReadingPipe(1, direccion);
  //radio.setPALevel(RF24_PA_MIN);
  radio.setDataRate(RF24_250KBPS);
  radio.startListening();
  
  //HABILITA DERECHA
  pinMode(ENA_DER, OUTPUT);  // ENA
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  
  //HABILITA DERECHA
  pinMode(ENB_IZQ, OUTPUT);  // ENB
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  
  
}
 
void loop(){
  
  if (radio.available()){    
     radio.read(velocidad, sizeof(velocidad)); //Leemos los datos y los guardamos en la variable velocidad
  }
  
  v_der = velocidad[1];
  v_izq = velocidad[0];

 

  if (v_der > 100 && v_der<=200){
    v_der =(v_der - 100)*2 + 55;
    
  }else if (v_der > 0 && v_der<100) {
    v_der = (v_der - 100)*2 - 55;
  }
  else {
    v_der=0;
    }

  if (v_izq > 100 && v_izq<=200){
    v_izq = (v_izq - 100)*2 + 55;
  }
  else if (v_izq > 0 && v_izq<100) {
    v_izq = (v_izq - 100)*2 - 55;
  }
  else{v_izq=0;}

// Serial.print(v_izq);
 //Serial.print("\n");


  if(v_der > 55 && v_der <= 255){
   move_adelante(pinMotorA, v_der);
    
  }else if(v_der < -55 && v_der >= -255){
    move_atras(pinMotorA, v_der*(-1));
    
  }else if(v_der==0){
    stop(pinMotorA);
  }
  
   if(v_izq > 55 && v_izq <= 255){
    move_adelante(pinMotorB, v_izq);
    
  }else if(v_izq < -55 && v_izq >= -255){
    move_atras(pinMotorB, v_izq*(-1));
    
  }else if (v_izq==0){
    stop(pinMotorB);
  }

}

void move_adelante(const int pinMotor[3], int speed)
{
   digitalWrite(pinMotor[1], HIGH);
   digitalWrite(pinMotor[2], LOW);

   analogWrite(pinMotor[0], speed);
}

void move_atras(const int pinMotor[3], int speed)
{
   digitalWrite(pinMotor[1], LOW);
   digitalWrite(pinMotor[2], HIGH);

   analogWrite(pinMotor[0], speed);
}

void stop(const int pinMotor[3])
{
   digitalWrite(pinMotor[1], LOW);
   digitalWrite(pinMotor[2], LOW);

   analogWrite(pinMotor[0], 0);
}
