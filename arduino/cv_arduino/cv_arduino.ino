//https://dl.espressif.com/dl/package_esp32_index.json
#include <Wire.h>
#include <LMP91000.h>
//#include <Arduino.h>

LMP91000 lmp = LMP91000();

const double v_tolerance = 33;
byte moc1,moc2,moc3,moc4;
int S_Vol,E_Vol,Step,Freq,Cycle;
String chuoi="",chuoi1,chuoi2,chuoi3,chuoi4,chuoi5;
void setup() 
{  
  Wire.begin();
  Serial.begin(115200);
//  analogSetPinAttenuation(33, ADC_0db);
  analogReference(EXTERNAL);
  //enable the potentiostat
  delay(500);
  lmp.standby();
  delay(500);
  initLMP();
  delay(2000); //warm-up time for the sensor 
}


void loop() 
{                                    
  while(Serial.available()){
    chuoi=Serial.readString();;//doc chuoi
    
    
//chuoi="-500|600_2?25";

    for(int i=0;i<chuoi.length();i++){
      if(chuoi.charAt(i)=='|'){
        moc1=i; //tim vi tri ki tu "|"
        }
      if(chuoi.charAt(i)=='_'){
        moc2=i; //tim vi tri ki tu "_"
        }       
      if(chuoi.charAt(i)=='?'){
        moc3=i; //tim vi tri ki tu "?"
        }
      if(chuoi.charAt(i)=='#'){
        moc4=i; //tim vi tri ki tu "#"
        }                
      }
      //chuoibandau -200|600_2?25#1
      chuoi1=chuoi;
      chuoi2=chuoi;
      chuoi1.remove(moc1); //chuoi1=-200
      chuoi2.remove(0,moc1+1); // chuoi2=600\2?25#1
      chuoi3=chuoi2; //chuoi3=600\2?25
      chuoi2.remove(moc2-moc1-1);//chuoi2=600
      chuoi3.remove(0,moc2-moc1);//chuoi3=2?25#1
      chuoi4=chuoi3;//chuoi3=2?25#1
      chuoi3.remove(moc3-moc2-1);//chuoi3=2
      chuoi4.remove(0,moc3-moc2);//chuoi4=25#1
      chuoi5=chuoi4;//chuoi5=25#1
      chuoi4.remove(moc4-moc3-1);//chuoi4=25
      chuoi5.remove(0,moc4-moc3);//chuoi5=1


      
      S_Vol=chuoi1.toInt();
      E_Vol=chuoi2.toInt();
      Step=chuoi3.toInt();
      Freq=chuoi4.toInt();
      Cycle=chuoi5.toInt();
//            runCV(-200,600,10,25);
//            runCV(600,-200,10,25);
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

//Thí nghiệm 1: đổi biến freq từ double sang int: fail
//Thí nghiệm 2: đặt stepV và freq thành biến cục bộ sau đó gán bằng Step và Freq: fail
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
  delay(10);
  Serial.print(voltage);

  setBiasVoltage(voltage);

//  float tensao = lmp.getVoltage(analogRead(33), 3.3, 12);
//  float amperage = (tensao - 0.66) / 3500;

  float tensao = lmp.getVoltage(analogRead(A0), 3.3, 10);
  float amperage = (tensao - 0.66) / 3500;
  //Serial.print(", Vout(V): ");
  //Serial.print(tensao,5);
  //Serial.print(", Current(uA): ");
  //Serial.print(",");
//  Serial.print("|");
  Serial.print(";");
  Serial.println(amperage/pow(10,-6),5);


  delay(rate);
}

void runCVForward(int16_t startV, int16_t endV, int16_t stepV, double freq)

{
  for (int16_t j = startV; j <= endV; j += stepV)
  {
    biasAndSample(j,freq);
    //Serial.println();
  }
}


void runCVBackward(int16_t startV, int16_t endV, int16_t stepV, double freq)

{
  for (int16_t j = startV; j >= endV; j -= stepV)
  {
    biasAndSample(j,freq);
    //Serial.println();
  }
}
