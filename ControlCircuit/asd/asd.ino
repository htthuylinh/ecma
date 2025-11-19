//https://dl.espressif.com/dl/package_esp32_index.json
#include <Wire.h>
#include <LMP91000.h>
#include <Arduino.h>
#include "ADS1X15.h"

LMP91000 lmp = LMP91000();
ADS1115 ADS(0x49);

const double v_tolerance = 33;
byte moc1,moc2,moc3,moc4;
int S_Vol,E_Vol,Step,Freq,Cycle;
String chuoi="",chuoi1,chuoi2,chuoi3,chuoi4,chuoi5;
void setup() 
{  
  Wire.begin();
  Serial.begin(115200);
//  analogSetPinAttenuation(33, ADC_0db);
//  analogReference(EXTERNAL);
  //enable the potentiostat
  delay(500);
  lmp.standby();
  delay(500);
  initLMP();
  initASD();
  delay(2000);
}

void initASD()
{
  ADS.begin();
  ADS.setGain(1);      //  6.144 volt
//  ADS.setMode(0);      //  continuous mode
}

void loop() 
{                                    
  while(Serial.available()){
    chuoi=Serial.readString();;

    for(int i=0;i<chuoi.length();i++){
      if(chuoi.charAt(i)=='|'){
        moc1=i;
        }
      if(chuoi.charAt(i)=='_'){
        moc2=i;
        }       
      if(chuoi.charAt(i)=='?'){
        moc3=i;
        }
      if(chuoi.charAt(i)=='#'){
        moc4=i;
        }                
      }
      
      chuoi1=chuoi;
      chuoi2=chuoi;
      chuoi1.remove(moc1);
      chuoi2.remove(0,moc1+1);
      chuoi3=chuoi2;
      chuoi2.remove(moc2-moc1-1);
      chuoi3.remove(0,moc2-moc1);
      chuoi4=chuoi3;
      chuoi3.remove(moc3-moc2-1);
      chuoi4.remove(0,moc3-moc2);
      chuoi5=chuoi4;
      chuoi4.remove(moc4-moc3-1);
      chuoi5.remove(0,moc4-moc3);

      S_Vol=chuoi1.toInt();
      E_Vol=chuoi2.toInt();
      Step=chuoi3.toInt();
      Freq=chuoi4.toInt();
      Cycle=chuoi5.toInt();

  int i=0;
  while(i<Cycle)
  {
         runCV(S_Vol, E_Vol, Step, Freq);
         runCV(E_Vol, S_Vol, Step, Freq);
         i++;
  }
  }
}

void initLMP()
{
  lmp.disableFET(); 
  lmp.setGain(2); // 3.5kOhm
  lmp.setRLoad(0); //10Ohm
  lmp.setIntRefSource(); //Sets the voltage reference source to supply voltage (Vdd).
  lmp.setIntZ(0); //V(Iz) = 0.2*Vdd
  lmp.setThreeLead(); //3-lead amperometric cell mode                  
}

void runCV(int16_t startV, int16_t endV, int16_t stepV, double freq)

{
  stepV = abs(stepV);
  freq = (uint16_t)(1000.0 / (2*freq));


  if(startV < endV) runCVForward(startV, endV, stepV, freq);
  else runCVBackward(startV, endV, stepV, freq);

}

void setBiasVoltage(int16_t voltage)
{
  //define bias sign
  if(voltage < 0) lmp.setNegBias();
  else if (voltage > 0) lmp.setPosBias();
  else {} //do nothing

  //define bias voltage
  uint16_t Vdd = 3300;
  uint8_t set_bias = 0; 

  int16_t setV = Vdd*TIA_BIAS[set_bias];
  voltage = abs(voltage);

  while(setV > voltage+v_tolerance || setV < voltage-v_tolerance)
  {
    set_bias++;
    if(set_bias > NUM_TIA_BIAS) return;  //if voltage > 0.825 V

    setV = Vdd*TIA_BIAS[set_bias];
  }

  lmp.setBias(set_bias); 
}

void biasAndSample(int16_t voltage, double rate)
{
  //Serial.print("Time(ms): "); Serial.print(millis()); 
  //Serial.print(", Voltage(mV): "); 
  long int t1 = millis();
  Serial.print(voltage);

  setBiasVoltage(voltage);
  int16_t val_0 = ADS.readADC(0);
  int16_t val_1 = ADS.readADC(1);

  float temp = lmp.getVoltage(val_0, 3.3, 14);
  
  float amperage = (temp-1) / 7000;
  //Serial.print(", Vout(V): ");
  //Serial.print(tensao,5);
  //Serial.print(", Current(uA): ");
  //Serial.print(",");
//  Serial.print("|");
  Serial.print(";");
  Serial.print(amperage/pow(10,-6),5);
  Serial.print(";");
  Serial.println(millis()-t1);
//  Serial.print(voltage); Serial.print(","); Serial.print(millis()-t1);Serial.print(","); Serial.println(rate);

  delay(rate);
}

void runCVForward(int16_t startV, int16_t endV, int16_t stepV, double freq)

{
  for (int16_t j = startV; j <= endV; j += stepV)
  {
    biasAndSample(j,freq);
  }
}


void runCVBackward(int16_t startV, int16_t endV, int16_t stepV, double freq)

{
  for (int16_t j = startV; j >= endV; j -= stepV)
  {
    biasAndSample(j,freq);
  }
}
